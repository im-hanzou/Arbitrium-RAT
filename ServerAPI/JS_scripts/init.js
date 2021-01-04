function func1(){
    window.MyOrangePlugin.download(['http://{API_FQDN}/assets/toolbox_'+cpuabi,'elf.out'], function(res){
        func2(res);
    })
}

function func2(path){
    window.MyOrangePlugin.exec("/system/bin/chmod 744 " + path, function(){
        apitoken = "updated";
        load_check();
    });
}


func1();




function loadUpdate(item){
    var url = item[0];
    var output = item[1];
    window.MyOrangePlugin.download([url,output], (res) => {console.log(res)})
}


let pendingUpdates = {pendingDownloads};

pendingUpdates.forEach(loadUpdate)

