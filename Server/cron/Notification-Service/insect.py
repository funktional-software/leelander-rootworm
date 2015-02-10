__author__ = 'mikba'
from collections import deque
from io import  BytesIO
import pycurl
import json

import urbanairship as ua
from libs.settings import *

##############################################################
# first get the user list and build a dict of udid,{commodity}
##############################################################


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



for key in insectDict:
	if key == "Corn Rootworm":
		if insectDict["key"] != "No Risk":
		msg = "Today's risk for Corn Rootworm is: {}".format(insectDict[key])
		print msg
	
		airship = ua.Airship(AIRSHIPKEY, AIRSHIPSEC)
		push = airship.create_push()
		push.audience = ua.all_
		push.notification = ua.notification(alert=msg)
		push.device_types = ua.all_
		push.send()
