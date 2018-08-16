/**
 * Created by manuggz on 15/08/2018.
 */
/*global page_sin_plan */
$(function () {
    var btns_crear_pensum = $('.btn-crear-pensum');
    // Desactiva los botones de crear pensums cuando se presiona alguno para evitar errores con el backend
    btns_crear_pensum.click(function (ev) {
        btns_crear_pensum.addClass('disabled')
    });
});