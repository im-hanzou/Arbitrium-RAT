import requests, sys, time
import hashlib


'''
cmd_query = sys.argv[1]
deviceUUID = sys.argv[2]
ThreadID = sys.argv[3]
'''


def getRESP(taskid):
	resp_url = "http://{API_FQDN}/pingtask?hashid={}&token={}&taskid={}x{}".format(sys.argv[2],\
		customHash(sys.argv[2]), sys.argv[3], taskid)
	resp_, counter_wait = "0", 0
	while len(resp_)<2:
		resp_ = requests.get(resp_url).content
		counter_wait += 1
		if counter_wait > 90:
			return "0000"
		time.sleep(2)
	return resp_



def customHash(passwd):
	return hashlib.sha1("JYF&6rfvJY^R&D^P+';5r*"+passwd+"JYF&6rfvJY^R&D^P+;5r*").hexdigest()[20:]



def addCMD(cmd_query):
	url = "http://{API_FQDN}/addtask?hashid={}&token={}&cmd={}".format(sys.argv[2], \
		customHash(sys.argv[2]), cmd_query)
	for j in range(2):
		taskid = requests.get(url).content
		getRESP_re = getRESP(taskid)
		if getRESP_re != "0000":
			return getRESP_re



print addCMD(sys.argv[1])


