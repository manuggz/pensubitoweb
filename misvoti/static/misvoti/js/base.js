'use strict';
$(document).ready(function () {

    function showBackendMessagesToUser(){
        for(let i in misvotiapp.messages){
            var message = misvotiapp.messages[i]
            showMessage(message.text,message.level_tag,false)
        }
    }
    showBackendMessagesToUser();
});
