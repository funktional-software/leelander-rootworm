__author__ = 'mikba'
from collections import deque
from io import  BytesIO
import MySQLdb
import pycurl
import json
import time
import uuid
import os
import sys
import math
import datetime
import time

from settings import *
from commodityMap import *


def distance(latuser, lonuser, latplot, lonplot):	
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - latuser)*degrees_to_radians
    phi2 = (90.0 - latplot)*degrees_to_radians
        
    # theta = longitude
    theta1 = lonuser*degrees_to_radians
    theta2 = lonplot*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    miles = 3963 # per google, others say 3959
    return arc*miles



def gencommoditydictraw():
	data = BytesIO()

	c = pycurl.Curl()
	c.setopt(c.URL, COMMODITYURL)
	c.setopt(c.HEADER, False)
	#c.setopt(c.RETURNTRANSFER, 1)
	#c.setopt(c.HTTP_VERSION, CURL_HTTP_VERSION_1_1)
	c.setopt(c.WRITEFUNCTION, data.write)
	c.perform()

	commodityDictRaw = json.loads(data.getvalue())
	return commodityDictRaw


def genfuturesdictraw(tosend):
	capi = cmdtyApiHelper()

	futuresDict = dict()
	futuresUrl = COMMODITYURLBASE
	# get unique requests
	for userdid in tosend:
		for capidict in tosend[userdid]["futures"]:
			fdkey = capi.getFDKey(capidict)
		 	futuresDict[fdkey] = ""

	futuresUrl += ",".join(futuresDict)

	# get the data
	data = BytesIO()

	c = pycurl.Curl()
	c.setopt(c.URL, futuresUrl)
	c.setopt(c.HEADER, False)
	#c.setopt(c.RETURNTRANSFER, 1)
	#c.setopt(c.HTTP_VERSION, CURL_HTTP_VERSION_1_1)
	c.setopt(c.WRITEFUNCTION, data.write)
	c.perform()

	futuresDictRaw = json.loads(data.getvalue())
	return futuresDictRaw

def queuesimplealert(msg, token, os, clientId, source, counter):
	q = alertqueue()
	msgdata = {"message":msg,"token":token,"os":os,"clientId":clientId}
	alertid = token+os+clientId+source+datetime.datetime.now().strftime("%d-%m-%y")+str(counter)

	q.putalert(msgdata, alertid)



def queuecommodityalerts(tosend, commodityDict, futuresDict, sendtype):
	q = alertqueue()
	capi = cmdtyApiHelper()

	# loop through users
	#     send to queue
	for udid in tosend:
		msgs = list()	
		for cmdtytoken in tosend[udid]["commodities"]:
			if cmdtytoken in commodityDict:
				msg = "{}\n".format(commodityDict[cmdtytoken])
				msgs.append(msg)


		for futrdict in tosend[udid]["futures"]:
			fdkey = capi.getFDKey(futrdict)
			if fdkey in futuresDict and len(futuresDict[fdkey]) > 0:
				msg = "{}\n".format(futuresDict[fdkey])
				msgs.append(msg)
		
		counter = 0
		for apnsmsg in msgs:
			msgdata = {"message":apnsmsg,"token":tosend[udid]["token"],"os":tosend[udid]["os"],"clientId":tosend[udid]["enterprise"]}
			alertid = tosend[udid]["token"]+tosend[udid]["os"]+tosend[udid]["enterprise"]+sendtype+datetime.datetime.now().strftime("%d-%m-%y")+str(counter)
			counter += 1
			q.putalert(msgdata, alertid)
		# log the activity
		db = database()
		db.update("call sp_log_push_activity('"+sendtype+"', '"+str(counter)+"');")

			

def genreglist():
	tosend = {}
	curUdid = ""
	db = database()
	# create a dict of udid: dict of os, token, list of commodities
	# for row in db.select("select c.udid, c.commodityName, d.os, d.token, d.clientId, c.enableDaily, c.futureMonth, c.futureYear from commodities_constraints as c inner join device_information as d on c.udid = d.udid where c.openAlert = 1 order by c.udid").fetchall():
	for row in db.select("call sp_get_devices_new();").fetchall():
		if curUdid != row[0]:
			curUdid = row[0]
			if curUdid not in tosend:
				tosend[curUdid] = dict(os=row[1], clientId=row[2], token=row[3])

	return tosend



def setRegistered(udid):
	db = database()
	db.update("call sp_set_devices_registered('"+udid+"');")




def gensendlist(sproc):
	tosend = {}
	curUdid = ""
	db = database()
	# create a dict of udid: dict of os, token, list of commodities
	# for row in db.select("select c.udid, c.commodityName, d.os, d.token, d.clientId, c.enableDaily, c.futureMonth, c.futureYear from commodities_constraints as c inner join device_information as d on c.udid = d.udid where c.openAlert = 1 order by c.udid").fetchall():
	for row in db.select(sproc).fetchall():
		if curUdid != row[0]:
			curUdid = row[0]
			if curUdid not in tosend:
				tosend[curUdid] = dict(os=row[2], token=row[3], enterprise=row[4], commodities=deque(), futures=deque())
	    
	    # if user has selected current month, or due to UI failed so select it but has no future
		if row[5] == 1 or row[6] == 0:	
			tosend[curUdid]["commodities"].append(row[1])
		
		# if future month and year are set
		if row[6] > 0 and row[7] > 0:
			tosend[curUdid]["futures"].append(dict(name=row[1],month=row[6],year=row[7]))

	return tosend




class alertqueue(object):
	def __init__(self):		
		if not os.path.exists('./pending/'):
		    os.makedirs('./pending/')
		if not os.path.exists('./errors/'):
		    os.makedirs('./errors/')
		self.__path = './pending/'

	def putalert(self, jsontext, idstr):
		fname = self.__path + idstr
		if not os.path.isfile(fname):
			with open(fname, 'w') as outfile:
  				json.dump(jsontext, outfile)


class database(object):
	def __init__(self):
		# create a db connection
		self.__db = MySQLdb.connect(host=DBSERVER, # your host, usually localhost
          user=DBUSER, # your username
          passwd=DBPWD, # your password
          db=DBNAME) # name of the data base


	def select(self, tsql):
		cur = self.__db.cursor() 
		cur.execute(tsql)
		
		return cur

	def update(self, tsql):
		cur = self.__db.cursor() 

		try:
			cur.execute(tsql)
			self.__db.commit()
		except:
			self.__db.rollback()

		cur.close()

