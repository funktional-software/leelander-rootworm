__author__ = 'mikba'
import urbanairship as ua
from libs.settings import *

import os.path

#if os.path.isfile("/var/www/web/content/GRMTest/pending_message"):
if os.path.isfile("/var/www/html/GRMTest/pending_message"):
	print "sending test message"
	airship = ua.Airship(AIRSHIPKEY, AIRSHIPSEC)
	push = airship.create_push()
	push.audience = ua.all_
	push.notification = ua.notification(alert="GRM Test message")
	push.device_types = ua.all_
	push.send()

	os.remove("/var/www/html/GRMTest/pending_message")
