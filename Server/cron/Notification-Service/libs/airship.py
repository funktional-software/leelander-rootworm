import json
import sys
import requests

import urbanairship as ua
from utils import *

class airship(object):
	def __init__(self):		
		self.__keys = dict()
		db = database()
		cur = db.select("select clientId, AppKey, AppCredential from site_config")
		for row in cur.fetchall():
			keystr = row[0] 
			self.__keys[keystr] = (row[1], row[2])


	def emit(self, jsontext):
		tosend = json.loads(jsontext)
		userkey = tosend["clientId"]

		airkey = ""
		airsec = ""

		try:
			keytuple = self.__keys[userkey]
			airkey = keytuple[0]
			airsec = keytuple[1]
		except KeyError, e:
			print "ERROR: invalid airship target " + userkey
			return False

		try:
			airship = ua.Airship(airkey, airsec)
			push = airship.create_push()

			if tosend["os"] == "android":
				push.audience = ua.apid(tosend['token'])
			else:
				push.audience = ua.device_token(tosend['token'])

			push.notification = ua.notification(alert=tosend['message'])
			push.device_types = [tosend["os"]]
			print push.send()
			return True

		except:
			print "Unexpected error:", sys.exc_info()[0]
			return False

	def register(self, udid, os, clientId, token):
		userkey = clientId

		airkey = ""
		airsec = ""

		try:
			keytuple = self.__keys[userkey]
			airkey = keytuple[0]
			airsec = keytuple[1]
		except KeyError, e:
			print "ERROR: invalid airship target " + userkey
			return False

		# airship code
		if os == "ios":
			airship = ua.Airship(airkey, airsec)
			airship.register(token, tags=[clientId,])
		elif os == "android":
			# bugbug todo consider replacing the UA lib or adding this to it's codebase
			url = 'https://go.urbanairship.com/api/apids/' + token
			payload = {"tags": [clientId]}

			r = requests.post(url, data=json.dumps(payload))
			
			#bugbug android partial impl
			print r
		return True
