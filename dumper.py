import urllib2
import urllib
import gzip
import os
import json
import sys
import time
import StringIO

__author__ = "Raghav Sood"
__copyright__ = "Copyright 2014"
__credits__ = ["Raghav Sood"]
__license__ = "CC"
__version__ = "1.0"
__maintainer__ = "Raghav Sood"
__email__ = "raghavsood@appaholics.in"
__status__ = "Production"

if len(sys.argv) <= 1:
	print "Usage:\n 	python dumper.py [conversation ID] [chunk_size (recommended: 2000)] [{optional} offset location (default: 0)]"
	print "Example conversation with Raghav Sood"
	print "	python dumper.py 1075686392 2000 0"
	sys.exit()

error_timeout = 30 # Change this to alter error timeout (seconds)
general_timeout = 7 # Change this to alter waiting time afetr every request (seconds)
messages = []
talk = sys.argv[1]
offset = int(sys.argv[3]) if len(sys.argv) >= 4 else int("0")
messages_data = "lolno"
end_mark = "\"payload\":{\"end_of_history\""
limit = int(sys.argv[2])
headers = {"origin": "https://www.facebook.com", 
"accept-encoding": "gzip,deflate", 
"accept-language": "en-US,en;q=0.8", 
"cookie": "datr=XdSrUygjD80dT9ik9WAiPPD6; lu=ghRQ682B9Guv6oilMKDxf_Bw; js_ver=1941; c_user=100000378864191; fr=0OfF0pSNokfZMxkBU.AWX3eNIAHBGyNsaDFyFkIAcx61M.BUGouh.Ky.FU9.0.AWUtc7gY; xs=119%3AQ1QyL9n5oXs43w%3A2%3A1422377708%3A20366; csm=2; s=Aa40jPmkI4TAd45W.BVPXSu; act=1430341853844%2F0; p=-2; presence=EM430342005EuserFA21B00378864191A2EstateFDsb2F1430335320722Et2F_5bDiFA2user_3a662640544A2ErF1C_5dElm2FA2user_3a662640544A2Euct2F1430309854613EtrFA2loadA2EtwF1541516167EatF1430341995817G430342005989CEchFDp_5f1B00378864191F5CC; wd=1366x383", 
"pragma": "no-cache", 
"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.122 Safari/537.36", 
"content-type": "application/x-www-form-urlencoded", 
"accept": "*/*", 
"cache-control": "no-cache", 
"referer": "https://www.facebook.com/messages/zuck"}

base_directory = "Messages/"
directory = base_directory + str(talk) + "/"
pretty_directory = base_directory + str(talk) + "/Pretty/"

try:
	os.makedirs(directory)
except OSError:
	pass # already exists

try:
	os.makedirs(pretty_directory)
except OSError:
	pass # already exists

while end_mark not in messages_data:

	data_text = {"messages[user_ids][" + str(talk) + "][offset]": str(offset), 
	"messages[user_ids][" + str(talk) + "][limit]": str(limit), 
	"client": "web_messenger", 
	"__user": "100000378864191", 
	"__a": "1", 
	"__dyn": "7nmajEyl2lm9r88DgDxiWOGeFDzECiq78hAKGhVoyupFLHwxBxvyUWdwIhEoyUnwPUS2O4K5ebAxacFoydCxuFE", 
	"__req": "k", 
	"fb_dtsg": "AQEF5m6xMNcT", 
	"ttstamp": "265816970531095412077789984", 
	"__rev": "1712621"}
	data = urllib.urlencode(data_text)
	url = "https://www.facebook.com/ajax/mercury/thread_info.php"
	
	print "Retrieving messages " + str(offset) + "-" + str(limit+offset) + " for conversation ID " + str(talk)
	req = urllib2.Request(url, data, headers)
	response = urllib2.urlopen(req)
	compressed = StringIO.StringIO(response.read())
	decompressedFile = gzip.GzipFile(fileobj=compressed)
	
	
	outfile = open(directory + str(offset) + "-" + str(limit+offset) + ".json", 'w')
	messages_data = decompressedFile.read()
	messages_data = messages_data[9:]
	json_data = json.loads(messages_data)
	if json_data is not None and json_data['payload'] is not None:
		try:
			messages = messages + json_data['payload']['actions']
		except KeyError:
			pass #no more messages
	else:
		print "Error in retrieval. Retrying after " + str(error_timeout) + "s"
		print "Data Dump:"
		print json_data
		time.sleep(error_timeout)
		continue
	outfile.write(messages_data)
	outfile.close()	
	command = "python -mjson.tool " + directory + str(offset) + "-" + str(limit+offset) + ".json > " + pretty_directory + str(offset) + "-" + str(limit+offset) + ".pretty.json"
	os.system(command)
	offset = offset + limit
	time.sleep(general_timeout) 

finalfile = open(directory + "complete.json", 'wb')
finalfile.write(json.dumps(messages))
finalfile.close()
command = "python -mjson.tool " + directory + "complete.json > " + pretty_directory + "complete.pretty.json"
os.system(command)
