__author__ = 'mikba'
from collections import deque
from io import  BytesIO
import pycurl

from libs.settings import *
from libs.utils import *
from libs.commodityMap import *

##############################################################
# first get the user list and build a dict of udid,{commodity}
##############################################################
# setup a collector for msgs
tosend = {}
curUdid = ""
db = database()

# create a dict of udid: dict of os, token, list of bugs
cur = db.select("call sp_get_alerts_insect();").fetchall()
for row in cur:
    if curUdid != row[0]:
    	curUdid = row[0]
    	tosend[curUdid] = dict(os=row[4], token=row[5], enterprise=row[6], bugs=deque())
    tosend[curUdid]["bugs"].append(dict(type=row[1], low=row[2], high=row[3]))



# second get the bug values into a dict
data = BytesIO()

c = pycurl.Curl()
c.setopt(c.URL, INSECTURL)
c.setopt(c.HEADER, False)
#c.setopt(c.RETURNTRANSFER, 1)
#c.setopt(c.HTTP_VERSION, CURL_HTTP_VERSION_1_1)
c.setopt(c.WRITEFUNCTION, data.write)
c.perform()

insectDictRaw = json.loads(data.getvalue())

insectDict = dict()
for report in insectDictRaw["posts"]:
	# bugbug can these be plural?
	insectDict[report["bugs"][0]] = report["risk"][0]


# finally send em msgs
for udid in tosend:
	msgs = list()
	for bugdict in tosend[udid]["bugs"]:
		if bugdict["type"] in insectDict:
			reportedRisk = insectDict[bugdict["type"]]
			pushedRisk = "none"

			if bugdict["low"] == 1 and reportedRisk == "Low":
				pushedRisk = reportedRisk
			if bugdict["high"] == 1 and reportedRisk == "High":
				pushedRisk = reportedRisk

			if pushedRisk != "none":
				msg = "There is a {} Risk Alert for {}\n".format(pushedRisk, bugdict["type"])
				msgs.append(msg)
	

	counter = 0
	for msg in msgs:
		queuesimplealert(msg, tosend[udid]["token"], tosend[udid]["os"], tosend[udid]["enterprise"], "insect", counter)
		counter += 1
	# log the activity
	db.update("call sp_log_push_activity('insect', '"+str(counter)+"');")
