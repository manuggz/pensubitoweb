'use strict';
// Escape regex especial characters . => \\.
function escapeRegExp(str) {
    return str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
}

function block_js_element($elemen){
    if (1 !== $elemen.data('blockUI.isBlocked')) {
        $elemen.block({
            message: null,
            overlayCSS: {
                background: '#fff',
                opacity: 0.6
            }
        });
    }
}

/**
 * Show a message to the user
 * @param message
 * @param status
 * @param use_modal
 */
function showMessage(message,status = 'success',use_modal = true){
    alertify.notify(message, status, 5);
    // new Noty({
    //     type:status,
    //     timeout:3000,
    //     modal:use_modal,
    //     theme:'bootstrap-v3',
    //     text: message,
    // }).show();

}

// Extend js String adding a funcion that replace ALL ocurrences of search with replacement
// Something that's not for default with String.replace
String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(escapeRegExp(search), 'g'), replacement);
};

