import os
import shutil

from libs.airship import *

#grab files while they exist
morefiles = True
a = airship() 

while morefiles:
	# get first file and send
	files_in_dir = os.listdir("pending")
	if len(files_in_dir) > 0:
		filepart = files_in_dir[0:1][0]
		filepath = "pending/" + filepart
		errorpath = "errors/" + filepart
		if filepart == '.DS_Store':
			os.remove(filepath)
		else:
			with open (filepath, "r") as myfile:
				jsondata=myfile.read().replace('\n', '')
				#bugbug todo error handling
				if a.emit(jsondata):
					os.remove(filepath)
				else:
					shutil.move(filepath, errorpath)
	else:
		morefiles = False

