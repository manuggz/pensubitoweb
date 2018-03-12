/*
 * Author: Manuel González
 * Date: 12 Marzo 2018
 * Description:
 *      Código encargado de controlar el modal de agregar/editar una materia
 **/
/*global modal_materia_js_params*/
/*global modificar_plan_params */
$(function () {

    'use strict';
    /* Referencia al modal de la materia*/
    const $modal_agregar_mat = $("#modal-materia");

    /* Referencia al Select para el nro de creditos de la materia*/
    const $select_creditos_en_modal = $modal_agregar_mat.find("#select_creditos");
    /*Referencia al Text Input donde introducir el código de la materia*/
    const $txt_input_codigo_mat_en_modal = $modal_agregar_mat.find("#input_codigo_mat");
    /*Referencia al Text Input donde introducir el nombre de la materia*/
    const $txt_input_nombre_mat_en_modal = $modal_agregar_mat.find("#input_nombre_materia");
    /*Referencia al Select para seleccionar el tipo de la materia*/
    const $select_tipo_mat_en_modal = $modal_agregar_mat.find("#select_tipo_materia");

    /**
     * Los dropdown son listas que se muestran debajo de algunos Text Input con opciones
     * de autocompletación del campo.
     * */
    /*Dropdown para mostrar codigos de materias debajo del Text Input Código*/
    const $dowpdown_opciones_codigos = $("datalist[id='codigos']");
    /*Dropdown para mostrar nombres de materias debajo del Text Input Nombre*/
    const $dowpdown_opciones_materias_nombres = $("datalist[id='nombres_mat']");

    /*Boton principal del Modal, puede ser "Agregar Materia" | "Guardar Cambios"*/
    /*La acción del botón es indicada en la carga del modal*/
    const $btn_accion = $modal_agregar_mat.find("#btn-accion-materia");

    /**
     * Los trimestres del plan actual son guardados en un array:
     *      modificar_plan_params.plan_creado_json.trimestres
     * Esta variable indice_trimestre indica el index del trimestre al que pertenece la materia que se está editando o al trimestre
     * que pertenecera la nueva materia.
     * */
    let indice_trimestre;
    /**
     * Las materias para el trimestre actual son guardadas en un array:
     *      modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias
     * Esta variable indice_materia  indica el index de la materia que se está editando o el futuro index de la nueva materia.
     */
    let indice_materia;

    let $trimestre_box;
    let tr_trimestre;
    let accion;

    let errores_en_campos = false;


    function resetearDefaultInputs() {
        $select_creditos_en_modal.selectpicker('val', '');
        $select_tipo_mat_en_modal.selectpicker('val', '');
        $txt_input_nombre_mat_en_modal.val('');
        $txt_input_codigo_mat_en_modal.val('');
        $modal_agregar_mat.find("#select_nota_final").selectpicker('val', '');
    }

    $modal_agregar_mat.on('show.bs.modal', function (event) {

        const botonTrigger = $(event.relatedTarget);

        tr_trimestre = botonTrigger.closest('tr');

        $trimestre_box = botonTrigger.closest("div.box");
        indice_trimestre = parseInt($trimestre_box.data("trimestre-codigo"));

        accion = botonTrigger.data('action') || "agregar";

        $modal_agregar_mat.find(".modal-title").html(
            "Trimestre: " +
            convertir_periodo_codigo_a_string(modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].periodo) + " " +
            modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].anyo
        );

        limpiarMensajesErrorCampos();

        if (accion === "agregar") {

            indice_materia = modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias.length;

            resetearDefaultInputs();

            $btn_accion.html("¡Agregar Materia!");
        } else if (accion === "editar") {

            indice_materia = parseInt(tr_trimestre.data('materia-codigo'));
            let materia_json = modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias[indice_materia];

            $select_creditos_en_modal.selectpicker('val', materia_json.creditos);
            $select_tipo_mat_en_modal.selectpicker('val', materia_json.tipo);
            $txt_input_nombre_mat_en_modal.val(materia_json.nombre);
            $txt_input_codigo_mat_en_modal.val(materia_json.codigo);
            if (materia_json.esta_retirada !== undefined) {
                if (!materia_json.esta_retirada) {
                    $modal_agregar_mat.find("#select_nota_final").selectpicker('val', materia_json.nota_final);
                } else {
                    $modal_agregar_mat.find("#select_nota_final").selectpicker('val', 'R');
                }
            } else {
                $modal_agregar_mat.find("#select_nota_final").selectpicker('deselectAll');
            }

            $btn_accion.html("¡Guardar Cambios!");
        } else {
            console.log("Error abriendo Modal Materia: accion=", accion, " desconocida!");
            event.preventDefault();
        }

        $btn_accion[0].className = "btn btn-primary";

    });


    $btn_accion.click(function (event) {

        errores_en_campos = false;

        campos_validar.each(function (index, element) {
            limpiarErrorCampo(index, element);
            const jqCampo = $(this);
            validarCampo(jqCampo);
        });

        if (errores_en_campos) {
            event.preventDefault();
            return;
        }
        $btn_accion[0].className = "btn btn-success";

        let materia_json = {};
        materia_json.codigo = $txt_input_codigo_mat_en_modal.val();
        materia_json.nombre = $txt_input_nombre_mat_en_modal.val();
        materia_json.creditos = parseInt($select_creditos_en_modal.val());
        materia_json.tipo = $select_tipo_mat_en_modal.val();

        const val_nota = $modal_agregar_mat.find("#select_nota_final").val();

        materia_json.esta_retirada = val_nota === 'R';
        if (!materia_json.esta_retirada) {
            materia_json.nota_final = parseInt(val_nota);
        }

        $modal_agregar_mat.modal("hide");

        //var n_materias = modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias.length;
        modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias[indice_materia] = materia_json;

        if (accion === "agregar") {
            const nuevo_tr_mat_jquer = $(crear_html_tr_materia(indice_trimestre, indice_materia)).hide();
            nuevo_tr_mat_jquer.find(".selectpicker").selectpicker('refresh');

            $trimestre_box.find("tbody.materias-trimestres").append(nuevo_tr_mat_jquer);

            nuevo_tr_mat_jquer.show('slow');
        } else {
            const tds = tr_trimestre.find("td");

            const codigo_td = $(tds[0]);

            if (materia_json.codigo) {
                codigo_td.html(materia_json.codigo);
            } else {
                codigo_td.html("<abbr title='Sin Definir '>Sin.Definir.</abbr> </td>");
            }

            const nombre_td = $(tds[1]);

            if (materia_json.nombre) {
                nombre_td.html(materia_json.nombre);
            } else {
                nombre_td.html("<abbr title='Sin Definir '>Sin.Definir.</abbr> </td>");
            }

            $(tds[2]).html(convertir_tipo_materia_codigo_a_string(materia_json.tipo));
            $(tds[3]).html(materia_json.creditos);

            if (!materia_json.esta_retirada) {
                $(tds[4]).find(".selectpicker").selectpicker('val', materia_json.nota_final);
            } else {
                $(tds[4]).find(".selectpicker").selectpicker('val', 'R');
            }

        }

        actualizar_datos_plan_creado();

        btn_guardar_cambios.text("Guardar Cambios*");
        btn_guardar_cambios.removeAttr("disabled");

    });
    $txt_input_codigo_mat_en_modal.on('input', function (e) {
        $.get(modal_materia_js_params.url_ajax_get_materias, {
                codigo: $txt_input_codigo_mat_en_modal.val(),
                max_length: 5,
            },
            function (data, status) {
                if (status === "success") {
                    if (data.materias.length === 1 && data.materias[0].codigo === $txt_input_codigo_mat_en_modal.val()) {
                        $select_creditos_en_modal.selectpicker('val', data.materias[0].creditos);
                        $txt_input_nombre_mat_en_modal.val(data.materias[0].nombre);
                    } else {
                        let html_dropdown = '';
                        for (let i in data.materias) {
                            html_dropdown += '<option value="' + data.materias[i].codigo + '">' + data.materias[i].codigo + " - " + data.materias[i].nombre + '</option>';
                        }
                        $dowpdown_opciones_codigos.html(html_dropdown);
                    }
                } else {
                    console.log("Ocurrió un error obteniendo materias");
                }
            }
        );
    });
    $txt_input_nombre_mat_en_modal.on('input', function (e) {
        $.get(modal_materia_js_params.url_ajax_get_materias, {
                nombre: $txt_input_nombre_mat_en_modal.val(),
                max_length: 5,
            },
            function (data, status) {
                if (status === "success") {
                    if (data.materias.length === 1 && data.materias[0].nombre === $txt_input_nombre_mat_en_modal.val()) {
                        $select_creditos_en_modal.selectpicker('val', data.materias[0].creditos);
                        $txt_input_codigo_mat_en_modal.val(data.materias[0].codigo);
                    } else {
                        let html_dropdown = '';
                        for (let i in data.materias) {
                            html_dropdown += '<option value="' + data.materias[i].nombre + '">' + data.materias[i].codigo + " - " + data.materias[i].nombre + '</option>';

                        }
                        $dowpdown_opciones_materias_nombres.html(html_dropdown);
                    }
                } else {
                    console.log("Ocurrió un error obteniendo materias");
                }
            }
        );
    });


    const form_validar = $("form[data-togle='validator']");
    var campos_validar = form_validar.find("input,select");

    function limpiarErrorCampo(index, campo) {
        var jqCampo = $(campo);

        var container = jqCampo.closest("div.form-group");
        var jqMensajes = container.find("div.validate-errors ul");
        var jqIcono = container.children("span.glyphicon");

        container[0].className = "form-group";
        if (jqIcono.length > 0) {
            jqIcono[0].className = " glyphicon form-control-feedback ";
            container[0].className += " has-feedback";
        }

        jqMensajes.html("");

    }

    function limpiarMensajesErrorCampos() {
        campos_validar.each(limpiarErrorCampo);
    }

    function validarCampo(jqCampo) {
        var container = jqCampo.closest("div.form-group");
        var jqIcono = container.children("span.glyphicon");

        var state = "success";
        var mensaje_error = "";

        var pattern_valid = jqCampo.data('validator-pattern');

        if (pattern_valid != undefined) {
            if (!jqCampo.val().match(pattern_valid)) {
                state = "error";
                mensaje_error = jqCampo.data('validator-pattern-mensage') || "¡El campo contiene campos inválidos!";
                agregarErrorCampo(jqCampo, mensaje_error);
            }
        }

        var f_valid = jqCampo.data("validator-function");

        if (f_valid != undefined) {
            f_valid = window[jqCampo.data("validator-function")];
        }

        if (typeof f_valid === 'function') {
            var resultado = f_valid(jqCampo.val());
            if (resultado.es_valido) {
                state = "success";
            } else {
                state = "error";
                for (var i in resultado.errores) {
                    agregarErrorCampo(jqCampo, resultado.errores[i]);
                }
            }
        }

        if (jqCampo.prop('required') && jqCampo.val() === "") {
            state = "error";
            agregarErrorCampo(jqCampo, '¡Este campo es obligatorio!');
        }

        if (jqIcono.length > 0) {
            if (state === "error") {
                jqIcono[0].className += " glyphicon-remove";
            } else {
                jqIcono[0].className += " glyphicon-ok";
            }
        }

        //jqCampo.closest('form').es_valido = state != "error";
        container[0].className += " has-" + state;
        if (state == "error") {
            errores_en_campos = true;
            $btn_accion[0].className = "btn btn-danger";
        }

    }


    function iniciar_validar_form() {
        // Creamos los elementos en el DOM para colocar los errores
        campos_validar.each(function () {
            var dElement = $(this);

            var container = dElement.closest("div.form-group");

            //var ul_messagesobj = container.find("div.validate-errors ul");
            if (dElement.is('input')) {
                container.append('<span class="glyphicon form-control-feedback" aria-hidden="true"></span>');
                container.addClass("has-feedback");
            }
            container.append("<div class = 'help-block validate-errors'><ul></ul></div>");
        });

    }

    iniciar_validar_form();

    campos_validar.on('input', function (event) {
        limpiarErrorCampo(null, this);
        $btn_accion[0].className = "btn btn-primary";
    });

    function agregarErrorCampo(jqCampo, mensaje) {
        jqCampo.closest("div.form-group").find("div.validate-errors ul").append('<li>' + mensaje + '</li>');
    }

    campos_validar.change(function (event) {

        $btn_accion[0].className = "btn btn-primary";
        limpiarErrorCampo(null, this);
        var jqCampo = $(this);
        validarCampo(jqCampo);
    });

    function validar_codigo(codigo_str) {

        var resultado = {es_valido: true, errores: []};

        if (codigo_str == "") return resultado;

        if (!codigo_str.match(/^[A-Za-z]{2,4}-?\d{3,4}$/)) {
            resultado.es_valido = false;
            resultado.errores.push('¡Codigo incorrecto!');
            return resultado;
        }

        for (var j in modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias) {
            if (indice_materia != j && modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias[j].codigo == codigo_str) {
                resultado.es_valido = false;
                resultado.errores.push('¡No puedes agregar la materia dos veces en el mismo Trimestre!');
            }
        }

        return resultado;
    }

});