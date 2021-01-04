import time, subprocess, commands

runningProxies = []

with open('misc/initproxy.lst', 'w') as f:
	f.write('')


while True:
	fdata = []
	with open('misc/initproxy.lst', 'r') as f:
		fdata = f.readlines()
		fdata = [i.replace('\n', '') for i in fdata[:]]
	initList = []
	for i in fdata:
		if i not in runningProxies:
			initList.append(i)
		else:
			hashedID = i[i.index('-S')+3:].split(' ')[0]
			if "No Sockets found" in commands.getoutput("screen -ls %s"%hashedID):
				initList.append(i)
	if len(initList):
		print initList
	for j in initList:
		subprocess.Popen(j[5:], shell=True)
		runningProxies.append(j)
		time.sleep(1)
	time.sleep(2)
