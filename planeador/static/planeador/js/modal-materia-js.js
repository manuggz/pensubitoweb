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
    /**
     * Referencia al modal de la materia
     * @type {jQuery}
     */
    const $modal_agregar_mat = $("#modal-materia");
// Enlaza el DOM del boton que se presiona para actualizar los datos del plan del servidor
    var $btn_guardar_cambios = $("#btn-guardar-cambios");
    /**
     * Referencia al Select para el nro de creditos de la materia
     * @type {jQuery}
     */
    const $select_creditos_en_modal = $modal_agregar_mat.find("#select_creditos");
    /**
     * Referencia al Text Input donde introducir el código de la materia
     * @type {jQuery}
     */
    const $txt_input_codigo_mat_en_modal = $modal_agregar_mat.find("#input_codigo_mat");
    /**
     * Referencia al Text Input donde introducir el nombre de la materia
     * @type {jQuery}
     */
    const $txt_input_nombre_mat_en_modal = $modal_agregar_mat.find("#input_nombre_materia");
    /**
     * Referencia al Select para seleccionar el tipo de la materia
     * @type {jQuery}
     */
    const $select_tipo_mat_en_modal = $modal_agregar_mat.find("#select_tipo_materia");

    /**
     * Los dropdown son listas que se muestran debajo de algunos Text Input con opciones
     * de autocompletación del campo.
     * */
    /**
     *Dropdown para mostrar codigos de materias debajo del Text Input Código
     * @type {jQuery}
     */
    const $dowpdown_opciones_codigos = $("datalist[id='codigos']");
    /**
     * Dropdown para mostrar nombres de materias debajo del Text Input Nombre
     * @type {jQuery}
     */
    const $dowpdown_opciones_materias_nombres = $("datalist[id='nombres_mat']");

    /**
     * Boton principal del Modal, puede ser "Agregar Materia" | "Guardar Cambios"
     * La acción del botón es indicada en la carga del modal
     * @type {jQuery}
     */
    const $btn_accion = $modal_agregar_mat.find("#btn-accion-materia");

    /**
     * Los trimestres del plan actual son guardados en un array:
     *      modificar_plan_params.plan_creado_json.trimestres
     * Esta variable indice_trimestre indica el index del trimestre al que pertenece la materia que se está editando o al trimestre
     * que pertenecera la nueva materia.
     * @type {int}
     * */
    let indice_trimestre;
    /**
     * Las materias para el trimestre actual son guardadas en un array:
     *      modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias
     * Esta variable indice_materia  indica el index de la materia que se está editando o el futuro index de la nueva materia.
     * @type {int}
     */
    let indice_materia;

    /**
     * Referencia al elemento HTML <div class="card"... que contiene los datos del trimestre.
     * Se referencia cuando se carga el modal.
     * @type {jQuery}
     */
    let $trimestre_card;
    /**
     * Referencia al elemento HTML  <tr><td>MA1111</td><td>Matemáticas I</td>... que contiene los datos actuales de la materia a
     * editar.
     * Aunque solo se utiliza para obtener el atributo data-materia-codigo del tr, el cual nos indica el index de la
     * materia a editar en el array de materias.
     * @type {jQuery}
     */
    let $materia_tr;
    /**
     * Acción con la que se abre el modal , puede ser:
     *   "editar"  : Indica que se editará una materia
     *   "agregar" : Indica que se creará una nueva materia
     * @type {string}
     */
    let accion;

    /**
     * Referencia
     * @type {jQuery}
     */
    const $form_materia = $modal_agregar_mat.find("form[data-togle='validator']");
    const $campos_form_materia = $form_materia.find("input,select");
    /**
     * Vacia los controles del modal
     */
    function resetearDefaultInputs() {
        $select_creditos_en_modal.selectpicker('val', '');
        $select_tipo_mat_en_modal.selectpicker('val', '');
        $txt_input_nombre_mat_en_modal.val('');
        $txt_input_codigo_mat_en_modal.val('');
        $modal_agregar_mat.find("#select_nota_final").selectpicker('val', '');
    }

    /**
     * Cuando se carga el modal, se configuran los controles del modal para que el usuario pueda
     * realizar la "acción" de "editar" o "agregar" un trimesre.
     */
    $modal_agregar_mat.on('show.bs.modal', function (event) {
        /**
         * Botón que abrió el modal
         * @type {jQuery}
         */
        const $botonTrigger = $(event.relatedTarget);
        // HTML Card que contiene el trimestre al que pertenece o pertenecerá la materia
        $trimestre_card = $botonTrigger.closest("div.card");
        // Index del trimestre en el array de trimestres del plan
        indice_trimestre = parseInt($trimestre_card.data("trimestre-codigo"));
        // Acción con la que se abrió el modal
        accion = $botonTrigger.data('action') || "agregar";
        // Establece el título del modal al titulo del trimestre de la materia
        // Ejemplo: Septiembre - Diciembre 2020
        $modal_agregar_mat.find(".modal-title").html( "<h6>" +
            convertirPeriodoCodigoAString(modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].periodo) + " " +
            modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].anyo + "</h6>"
        );
        // Quitamos mensajes de error que estén en el modal para cada campo
        $campos_form_materia.each(limpiarErrorCampo);

        // Dependiendo de la acción con la que se abrió el modal configuramos los controles
        if (accion === "agregar") {
            //  Si vamos a agregar una materia, el index de la nueva materia es el tamaño actual del array de materias
            indice_materia = modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias.length;
            // Quitamos el contenido previo de los controles del modal
            resetearDefaultInputs();
            $btn_accion.html("¡Agregar Materia!");
        } else if (accion === "editar") {
            // Si vamos a editar una materia, buscamos el <tr> que contiene sus datos
            $materia_tr = $botonTrigger.closest('tr');
            // obtenemos su index en el array de materias
            indice_materia = parseInt($materia_tr.data('materia-codigo'));
            // Obtenemos el JSON con loEss datos actuales de la materia
            let materia_json = modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias[indice_materia];
            /**
             * Establecemos los valores de los controles para que representen los atributos de la materia
             */
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
        // Cuando se cierra el modal al realizar la acción con éxito, se cambia la clase a btn btn-success. Así que
        // hay que resetearla cuando se abre el modal.

    });

    /**
     * Realizamos la acción asociada al modal, cuando el usuario clickea el botón "acción" : "editar" , "agregar".
      */
    $btn_accion.click(function (event) {

        // Dice si alguno de los campos tiene errores
        let errores_en_campos = false;
        // Alguno de los campos tiene errores?
        $campos_form_materia.each(function (index, element) {
            limpiarErrorCampo(index, element);
            const $jqCampo = $(this);
            if(!isFieldValid($jqCampo)){
                errores_en_campos = true;
            }
        });

        if (errores_en_campos) {
            // Si algún campo tiene error, evitamos que se cierre el modal y no continuamos.
            event.preventDefault();
            return;
        }

        // Creamos el JSON con los datos de la nueva materia o la materia editada
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

        modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias[indice_materia] = materia_json;

        if (accion === "agregar") {
            // Creamos el nuevo <tr> con la materia a agregar
            const $nuevo_tr_mat_jquer = $(crearHtmlTrMateria(indice_trimestre, indice_materia)).hide();
            $nuevo_tr_mat_jquer.find(".selectpicker").selectpicker('refresh');

            // Agregamos el <tr> de la materia
            $trimestre_card.find("tbody.materias-trimestres").append($nuevo_tr_mat_jquer);

            $nuevo_tr_mat_jquer.show('slow');
        } else {

            // Buscamos los <td> con la información actual de la materia editada
            const $tds = $materia_tr.find("td");

            /**
             * El orden es <td>código | <td>nombre |<td>tipo|<td>creditos| <td> nota | <td> acciones
             * @type {jQuery|HTMLElement}
             */
            const $codigo_td = $($tds[0]);

            if (materia_json.codigo) {
                $codigo_td.html(materia_json.codigo);
            } else {
                $codigo_td.html("<abbr title='Sin Definir '>Sin.Definir.</abbr> </td>");
            }

            const $nombre_td = $($tds[1]);

            if (materia_json.nombre) {
                $nombre_td.html(materia_json.nombre);
            } else {
                $nombre_td.html("<abbr title='Sin Definir '>Sin.Definir.</abbr> </td>");
            }

            $($tds[2]).html(convertirTipoMateriaCodigoAString(materia_json.tipo));
            $($tds[3]).html(materia_json.creditos);

            if (!materia_json.esta_retirada) {
                $($tds[4]).find(".selectpicker").selectpicker('val', materia_json.nota_final);
            } else {
                $($tds[4]).find(".selectpicker").selectpicker('val', 'R');
            }

        }

        // Actualizamos las estadisticas mostradas al usuario
        actualizarDatosPlanCreado();

        $btn_guardar_cambios.html("<i class=\"fa fa-save\"></i> Guardar Cambios*");
        $btn_guardar_cambios.removeAttr("disabled");

    });
    /**
     * Cuando el usuario cambia el código de  la materia se le muestra en un dropdown opciones de autollenar
     */
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

    /**
     * Cuando el usuario cambia el nombre de  la materia se le muestra en un dropdown opciones de autollenar
     */
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

    /**
     * Cuando el usuario cambio el contenido de los campos del modal, nos aseguramos que se quiten los mensajes de error
     */
    $campos_form_materia.on('input change', function (event) {
        limpiarErrorCampo(null, this);
        let $jqCampo = $(this);
        isFieldValid($jqCampo);
    });

    /**
     * Remueve mensajes de error en un campo del modal.
     * Quita el html generado cuando un campo tiene error
     * @param index Index del elemento en @var $campos_form_materia
     * @param campo simple HTML elemento representando el campo
     */
    function limpiarErrorCampo(index, campo) {
        // JQuery referencia al campo
        let $jqCampo = $(campo);
        let $container = $jqCampo.closest("div.form-group");
        let $jqMensajes = $container.find("div.validate-errors ul");
        let $jqIcono = $container.children("span.glyphicon");

        $container[0].className = "form-group";
        if ($jqIcono.length > 0) {
            $jqIcono[0].className = " glyphicon form-control-feedback ";
            $container[0].className += " has-feedback";
        }

        $jqMensajes.html("");

    }

    /**
     * Checkea si el contenido de un campo es válido, si no lo le agrega un mensaje de error.
     * @param $jqCampo
     * @returns {boolean}
     */
    function isFieldValid($jqCampo) {
        let $container = $jqCampo.closest("div.form-group");
        let $jqIcono = $container.children("span.glyphicon");

        let state = "success";
        let mensaje_error = "";

        let pattern_valid = $jqCampo.data('validator-pattern');

        if (pattern_valid !== undefined) {
            if (!$jqCampo.val().match(pattern_valid)) {
                state = "error";
                mensaje_error = $jqCampo.data('validator-pattern-mensage') || "¡El campo contiene campos inválidos!";
                agregarErrorCampo($jqCampo, mensaje_error);
            }
        }
        let f_valid = $jqCampo.data("validator-function");

        if (f_valid !== undefined) {
            f_valid = window[$jqCampo.data("validator-function")];
        }

        if (typeof f_valid === 'function') {
            let resultado = f_valid($jqCampo.val());
            if (resultado.es_valido) {
                state = "success";
            } else {
                state = "error";
                for (let i in resultado.errores) {
                    agregarErrorCampo($jqCampo, resultado.errores[i]);
                }
            }
        }

        if ($jqCampo.prop('required') && $jqCampo.val() === "") {
            state = "error";
            agregarErrorCampo($jqCampo, '¡Este campo es obligatorio!');
        }

        if ($jqIcono.length > 0) {
            if (state === "error") {
                $jqIcono[0].className += " glyphicon-remove";
            } else {
                $jqIcono[0].className += " glyphicon-ok";
            }
        }

        //$jqCampo.closest('form').es_valido = state != "error";
        $container[0].className += " has-" + state;
        if (state === "error") {
            return false;
        }

        return true;
    }


    /**
     * Agrega un mensaje de error a un campo
     * @param $jqCampo
     * @param mensaje
     */
    function agregarErrorCampo($jqCampo, mensaje) {
        $jqCampo.closest("div.form-group").find("div.validate-errors ul").append('<li>' + mensaje + '</li>');
    }


    /**
     * Esta función es llamada cuando se cambia el valor del código
     * @param codigo_str
     * @returns {{es_valido: boolean, errores: Array}}
     */
    function validarCodigo(codigo_str) {
        let resultado = {es_valido: true, errores: []};

        if (codigo_str === "") return resultado;

        if (!codigo_str.match(/^[A-Za-z]{2,4}-?\d{3,4}$/)) {
            resultado.es_valido = false;
            resultado.errores.push('¡Codigo incorrecto!');
            return resultado;
        }

        for (let j in modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias) {
            if (indice_materia != j && modificar_plan_params.plan_creado_json.trimestres[indice_trimestre].materias[j].codigo === codigo_str) {
                resultado.es_valido = false;
                resultado.errores.push('¡No puedes agregar la materia dos veces en el mismo Trimestre!');
            }
        }

        return resultado;
    }

    //Hacemos global la función para que isFieldValid pueda acceder a élla utilizando window['validarCodigo'],
    window.validarCodigo = validarCodigo;
});