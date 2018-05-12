/*
 * Author: Manuel González
 * Date: 12 Marzo 2018
 * Description:
 *      Código encargado de controlar el modal de agregar trmiestre
 **/
/*global modificar_plan_params*/
$(function () {

    let $modal_agregar_trim = $("#modal-agregar-trim");
// Enlaza el DOM de la tabla en la que se mostrará el plan
    let $div_datos_trimestres_html = $("#div-trimestres");
// Enlaza el DOM del boton que se presiona para actualizar los datos del plan del servidor
    var $btn_guardar_cambios = $("#btn-guardar-cambios");
    let $select_periodo = $modal_agregar_trim.find("#id_select_periodo");
    let $select_anyo    = $modal_agregar_trim.find("#id_select_anyo");
    let orden_periodos = ['EM','AJ','JA','SD']

    function clear_selects() {
        $modal_agregar_trim.find("select").each(function (event) {
            var $div_container = $(this).closest('div.form-group');
            $div_container[0].className = "form-group";
            $div_container.find('div.help-block').html("")
        });

    }
    $modal_agregar_trim.on('show.bs.modal', function (event) {

        clear_selects();

        // Si el usuario no tiene trimestres en el plan
        // Se le coloca por default Septiembre - Diciembre del año actual
        if(modificar_plan_params.plan_creado_json.trimestres.length === 0){
            $select_periodo.val('SD');
            $select_anyo.val(new Date().getFullYear());
        }else{
            // Sino se le coloca por default el siguiente periodo al último creado
            var last_trim = modificar_plan_params.plan_creado_json.trimestres[modificar_plan_params.plan_creado_json.trimestres.length - 1];

            $select_periodo.val(orden_periodos[(orden_periodos.indexOf(last_trim.periodo) + 1) % orden_periodos.length]);
            if(last_trim.periodo === 'SD'){
                $select_anyo.val(parseInt(last_trim.anyo) + 1);
            }else{
                $select_anyo.val(last_trim.anyo);
            }
        }

    });

    $modal_agregar_trim.find("select").change(function (event) {
        var $div_container = $(this).closest('div.form-group');
        $div_container[0].className = "form-group";
        $div_container.find('div.help-block').html("")
    });

    $modal_agregar_trim.find('#btn-agregar-trim').click(function (event) {

        clear_selects();
        var anyo_seleccionado = parseInt($select_anyo.val());
        var $div_container;

        if(modificar_plan_params.plan_creado_json.trimestres.length > 0){
            var ultimo_trimestre = modificar_plan_params.plan_creado_json.trimestres[modificar_plan_params.plan_creado_json.trimestres.length - 1];

            if(ultimo_trimestre.anyo > anyo_seleccionado){
                $div_container = $select_anyo.closest('div.form-group');
                $div_container[0].className = "form-group has-error";
                $div_container.find('div.help-block').html("<p>¡Debe seleccionar el año del periodo anterior o el del siguiente!</p>")
                return;
            }else if(ultimo_trimestre.anyo === anyo_seleccionado){
                if(orden_periodos.indexOf(ultimo_trimestre.periodo) >= orden_periodos.indexOf($select_periodo.val())){
                    $div_container = $select_periodo.closest('div.form-group');
                    $div_container[0].className = "form-group has-error";
                    $div_container.find('div.help-block').html("<p>¡No puedes agregar un trimestre repetido o anterior!</p>")
                    return;
                }
            }
        }

        let nuevo_trim_js = {};
        nuevo_trim_js.materias = [];
        nuevo_trim_js.periodo = $select_periodo.val();
        nuevo_trim_js.anyo = $select_anyo.val();

        let n_trimestres = modificar_plan_params.plan_creado_json.trimestres.length;
        modificar_plan_params.plan_creado_json.trimestres[n_trimestres] = nuevo_trim_js;

        let $nuevo_trim_obj = $(crearHtmlBoxTrimestre(n_trimestres)).hide();
        $nuevo_trim_obj.appendTo($div_datos_trimestres_html);

        $nuevo_trim_obj.show('slow');

        actualizarDatosPlanCreado();

        $modal_agregar_trim.modal("hide");
        $btn_guardar_cambios.text("Guardar Cambios*");
        $btn_guardar_cambios.removeAttr("disabled");
    });

});