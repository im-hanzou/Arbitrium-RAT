import commands, base64
import re, sys
import subprocess



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


scanPorts = exeCMD('/data/data/net.orange.bolt/elf.out -w 1 -zv {} {} 2> /data/data/net.orange.bolt/netLogs && cat /data/data/net.orange.bolt/netLogs'.format(sys.argv[3], sys.argv[4]))


if "[{}]".format(sys.argv[3]) in scanPorts:
	print [i.split(' ')[0] for i in re.findall('\d+ \([a-zA-Z]+\) open', scanPorts)]
else:
	print [i.split(' ')[0] for i in re.findall('\d+ port \[*?tcp/[a-z*]+?\] succeeded', scanPorts)]

