import commands, base64
import re, sys
import subprocess
import time


def customBase64(encodedTxt, decode=1):
	replacements_ = [['+', 'plus'], ['/', 'slash'], ['=', 'equal']]
	if decode == -1:
		encodedTxt = base64.b64encode(encodedTxt).encode('ascii')
		for i in replacements_:
			encodedTxt = encodedTxt.replace(i[0], i[1])
		return encodedTxt
	for i in replacements_:
		encodedTxt = encodedTxt.replace(i[::-1][0], i[::-1][1])
	return base64.b64decode(encodedTxt).encode('ascii')



exeCMD = lambda cmd : commands.getoutput("python modules/runCMD.py {} {} {}".format(customBase64(cmd, -1), sys.argv[1], sys.argv[2])).replace('\n', '')
exeCMD_Popen = lambda cmd : subprocess.Popen("python modules/runCMD.py {} {} {}".format(customBase64(cmd, -1), sys.argv[1], sys.argv[2]),\
 shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


for k in range(5):
	ip_routes = exeCMD('ip route')

	current_ip = None
	for j in ip_routes.split('\n'):
		s = re.findall( r'[0-9]+(?:\.[0-9]+){3}', j)[-1]
		if '192.168.' in s:
			current_ip = s


	if not current_ip:
		for j in ip_routes.split('\n'):
			s = re.findall( r'[0-9]+(?:\.[0-9]+){3}', j)[-1]
			if 'wlan' in j.lower() or 'wlo' in j.lower():
				current_ip = s

	if current_ip:
		break


mask_ = '.'.join(current_ip.split('.')[:-1])
netIPs = []
try:
	start_ip, end_ip = sys.argv[3].split('-')
except:
	start_ip, end_ip = 1, 24
for i in range(int(start_ip), int(end_ip)):
	netIPs.append("ping -c 1 {} ; ".format(mask_ + '.' + str(i)))


base_cmd = 'ping -c 1 {}'
processes = []
baseCMD = "(" + ''.join(netIPs)[:-3] + ") > /data/data/net.orange.bolt/netLogsX | echo Hello"

exeCMD_Popen(baseCMD)

time.sleep(3)

output = exeCMD("cat /data/data/net.orange.bolt/netLogsX")

if "Reply from" in output:
	output = [i for i in output.split("Reply") if 'ttl=' in i.lower()]
else:	
	output = [i for i in output.split("PING") if 'bytes from' in i]

output = list(set([j[0] for j in [re.findall( r'[0-9]+(?:\.[0-9]+){3}', i) for i in output[:]] if len(j)]))


print output

