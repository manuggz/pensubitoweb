/**
 * Created by manuggz on 04/03/17.
 */
/*global modificar_plan_params */
$(function () {

// Enlaza el DOM de la tabla en la que se mostrará el plan
    var $div_datos_trimestres_html = $("#div-trimestres");
// Enlaza el dom del <fieldset> en el que se contienen todos los elementos con los que el usuario edita el plan
    var $fieldset = $("fieldset");
// Enlaza el DOM del boton que se presiona para actualizar los datos del plan del servidor
    var $btn_guardar_cambios = $("#btn-guardar-cambios");

    var $btn_float_guardar_cambios = $("#btn-float-guardar-cambios");


    /**
     * Redondea un numero ejem: 123.123453 a 4 cífras significativas a lo más. ejem: 123.1235
     * @param numero
     * @returns {number}
     */
    function redondear(numero) {
        return Math.round((numero + 0.00001) * 10000) / 10000;
    }

    $(".table.datos-materias-trimestre").DataTable( {
        "searching":   false,
        "paging":   false,
        "ordering": false,
        "info":     false,
        responsive: true,
        columnDefs: [
            { responsivePriority: 1, targets: 0 },
            { responsivePriority: 2, targets: -1 }
        ]
    } );

// Actualiza los indices(indice periodo e Indice acumulado) que se le muestra al usuario
// Básicamente recorre el JSON(modificar_plan_params.plan_creado_json) donde se guardan los datos de los trimestres
// A medida que lo va recorriendo va calculando y actualizando los datos que se le muestran al usuario
    function actualizarDatosPlanCreado() {
        // Nota: Recordar que el índice se calcula
        // sumatoria(nota(i)*creditomateria(i)) / sumatoria(creditosdemateria(i))
        // Si el estudiante pasa(nota >= 3) una materia previamente reprobada se anula la nota inmediata anterior

        // Contendrá la suma parcial nota(i)*creditomateria(i)
        var sum_nota_creds_acum = 0;

        // Total de creditos inscritos por el usuario
        // contiene creditos retirados,aprobados,reprobados
        var creds_inscri = 0;
        // Total de creditos retirados
        // Creditos inscritos que el estudiante retiró
        var creds_ret = 0;
        // Total de creditos aprobados
        // Creditos que el estudiante inscribió y aprobó con una nota mayor o igual a 3
        var creds_apro = 0;

        var n_materias_retiradas_total = 0;
        var n_materias_retiradas_trim_actual = 0;

        var n_materias_generales_total = 0;
        var n_materias_generales_trim_actual = 0;

        var n_materias_elec_area_total = 0;
        var n_materias_elec_libres_total = 0;

        // Total de creditos reprobados
        // Creditos que el estudiante inscribió y reprobó con una nota menor o igual a 2
        var creds_repro = 0;

        // Total de creditos que le cuentan en el cálculo del índice
        // Cuentan los creditos inscritos que no fueron retirados
        // y de las materias que no fueron anuladas debido a la regla que dice
        // que si apruebas una materia reprobada se anula la nota previamente anterior
        var creds_cont = 0;

        var indice_acumulado_actual;
        var indice_acumulado_anterior = 0;

        // Div.card que contiene los html elementos de un trimestre
        var $div_card_data;
        // Recorremos todos los trimestres
        // i tomará valores desde 0 hasta total(trimestres cursados)
        for (var i in modificar_plan_params.plan_creado_json.trimestres) {

            $div_card_data = $div_datos_trimestres_html.find('div.card[data-trimestre-codigo=' + i + ']');

            // Suma de nota(i)*creditosmateria(i) del trimestre actual del bucle
            // Se usa para calcular el indice del periodo/trimestre actual
            var sum_nota_creds_trimact = 0;
            // Total de los creditos que cuentan para el trimestre actual
            var cred_cont_trimact = 0;
            n_materias_retiradas_trim_actual = 0;
            n_materias_generales_trim_actual = 0;

            var trimestre_json = modificar_plan_params.plan_creado_json.trimestres[i];

            // Recorremos todas las materias inscritas para el trimestre i
            for (var j in trimestre_json.materias) {

                var materia_planeada = trimestre_json.materias[j];

                var cred_trim_actual = materia_planeada.creditos;

                // Aumentamos los creditos inscritos
                creds_inscri += cred_trim_actual;

                // Si la materia no está retirada
                if (!materia_planeada.esta_retirada) {

                    // Si la materia está reprobada
                    if (materia_planeada.nota_final <= 2) {
                        // Aumentamos los creditos reprobados
                        creds_repro += cred_trim_actual;
                    } else {

                        // Chequeamos si la materia ha sido reprobada anteriormente //

                        var nota_reprobada_anterior = -1; // -1 indica que no existe tal materia
                        // Recorremos todos los trimestres anteriores
                        for (var l = 0; l < i; l++) {
                            // Recorremos las materias para el trimestre l
                            for (var m in modificar_plan_params.plan_creado_json.trimestres[l].materias) {
                                // Si es la misma materia (comparamos el código)
                                if (modificar_plan_params.plan_creado_json.trimestres[l].materias[m].codigo == materia_planeada.codigo) {

                                    // Si la materia está reprobada y no está retirada
                                    // Significa que debemos anular esta nota
                                    if (modificar_plan_params.plan_creado_json.trimestres[l].materias[m].nota_final <= 2 && !modificar_plan_params.plan_creado_json.trimestres[l].materias[m].esta_retirada) {
                                        nota_reprobada_anterior = modificar_plan_params.plan_creado_json.trimestres[l].materias[m].nota_final;
                                    }
                                }
                            }
                        }

                        // Si se ha encontrado una nota que hay que anular
                        if (nota_reprobada_anterior != -1) {
                            // Descontamos lo que hemos sumado anteriormente
                            creds_cont -= cred_trim_actual;
                            sum_nota_creds_acum -= nota_reprobada_anterior * cred_trim_actual;
                        }

                        // Aumentamos los creditos aprobados
                        creds_apro += cred_trim_actual;

                        if(materia_planeada.tipo == "GE"){
                            n_materias_generales_trim_actual += 1;
                        }

                        if(materia_planeada.tipo == "EL"){
                            n_materias_elec_libres_total += 1;
                        }
                        if(materia_planeada.tipo == "EA"){
                            n_materias_elec_area_total += 1;
                        }
                    }

                    // Aumentamos la suma nota i x credito materia i
                    sum_nota_creds_trimact += materia_planeada.nota_final * cred_trim_actual;
                    // Aumentamos la suma de creditos para este trimestre
                    cred_cont_trimact += cred_trim_actual;

                } else {
                    // Aumentamos los creditos retirados
                    creds_ret += cred_trim_actual;
                    n_materias_retiradas_trim_actual += 1;
                }
            }


            if(n_materias_retiradas_trim_actual != trimestre_json.materias.length){
                n_materias_retiradas_total += n_materias_retiradas_trim_actual;
            }

            n_materias_generales_total += n_materias_generales_trim_actual;

            // Aumentamos la suma nota i * credito i para el acumulado
            sum_nota_creds_acum += sum_nota_creds_trimact;
            // Aumentamos la suma de creditos que cuentan totales
            creds_cont += cred_cont_trimact;
            // Actualizamos lo que se le muestra al usuario
            // Notar que se ha usado la notación #td-indice-<codigo trimestre> para referenciar el td que muestra
            // los datos para el trimestre <código trimestre>

            $div_card_data[0].className = "card";
            if (isNaN(sum_nota_creds_trimact) || sum_nota_creds_trimact === 0) {
                $div_card_data.find("#td-indice-periodo-" + i).html("Nota no calculable");
            } else {
                let indice_trimestre_red = redondear(sum_nota_creds_trimact / cred_cont_trimact);
                var html_indice_trimestre = "";
                if (indice_trimestre_red > 4.0) {
                    html_indice_trimestre += "<strong style='color: darkgreen;'>" + indice_trimestre_red + "</strong>"
                    $div_card_data[0].className += ' card-success';
                } else if (indice_trimestre_red < 2.9) {
                    html_indice_trimestre += "<strong style='color: darkred;'>" + indice_trimestre_red + "</strong>"
                    $div_card_data[0].className += ' card-danger';
                } else {
                    html_indice_trimestre += indice_trimestre_red
                }

                $div_card_data.find("#td-indice-periodo-" + i).html(html_indice_trimestre);
            }

            if (isNaN(sum_nota_creds_acum) || sum_nota_creds_acum === 0) {
                $div_card_data.find("#td-indice-acumulado-" + i).html("Nota no calculable");
            } else {

                indice_acumulado_actual = redondear(sum_nota_creds_acum / creds_cont);

                var html_indice_acumulado = "";
                if (indice_acumulado_actual > 4.0) {
                    html_indice_acumulado += "<strong style='color: green;'>" + indice_acumulado_actual + "</strong>"
                } else if (indice_acumulado_actual < 2.9) {
                    html_indice_acumulado += "<strong style='color: red;'>" + indice_acumulado_actual + "</strong>"
                } else {
                    html_indice_acumulado += indice_acumulado_actual
                }

                var diferencia = Math.abs(indice_acumulado_actual - indice_acumulado_anterior);
                if (diferencia < 0.0001) {
                    html_indice_acumulado += "<img src='" + modificar_plan_params.path_image_flecha_same + "' style='width:15px;height:15px;'/>"
                } else if (indice_acumulado_actual > indice_acumulado_anterior) {
                    html_indice_acumulado += "<img src='" + modificar_plan_params.path_image_flecha_up + "' style='width:15px;height:15px;'/>";
                    html_indice_acumulado += "(<strong style='color: limegreen;'>+" + redondear(diferencia) + "</strong>)"
                } else {
                    html_indice_acumulado += "<img src='" + modificar_plan_params.path_image_flecha_down + "' style='width:15px;height:15px;'/>";
                    html_indice_acumulado += "(<strong style='color: indianred;'>-" +  redondear(diferencia) + "</strong>)"
                }


                $div_card_data.find("#td-indice-acumulado-" + i).html(html_indice_acumulado);

                indice_acumulado_anterior = indice_acumulado_actual;
            }
        }

        $('#info-box-n-retiros').html(n_materias_retiradas_total + "/" + modificar_plan_params.plan_restricciones.n_max_retiros );
        $('#info-box-n-generales').html(n_materias_generales_total + "/" + modificar_plan_params.plan_restricciones.n_max_generales);
        $('#info-box-n-electivas-area').html(n_materias_elec_area_total + "/" + modificar_plan_params.plan_restricciones.n_max_electivas_area);
        $('#info-box-n-electivas-libre').html(n_materias_elec_libres_total + "/" + modificar_plan_params.plan_restricciones.n_max_electivas_libres);
    }

    /**
     * Callback para cuando se cambia la nota de una materia en la tabla
     * @param sel_obj Objeto al cual se le cambio la nota (this = select javascript)
     */
    function onChangeSelectNotaFinalMateria(sel_obj) {
        // Se ha hecho tal que en los tr del tbody de la tabla
        // se guarden datos usables para el código
        // por lo que lo primero es encontrar el más cernano tr del elemento
        var select = $(sel_obj);
        var tr_con_datos = select.closest("tr");
        var card_con_datos = tr_con_datos.closest("div.card");

        // Obtenemos los datos de la materia y trimestre a la cual pertenece
        var i_trimestre_cambiado = parseInt(card_con_datos.data("trimestre-codigo"));
        var j_materia_cambiada = parseInt(tr_con_datos.data("materia-codigo"));

        //var posicion_materia = posicion_ij_materia(i_trimestre_cambiado,j_materia_cambiada);
        var trimestre_json = modificar_plan_params.plan_creado_json.trimestres[i_trimestre_cambiado];
        var materia_json = trimestre_json.materias[j_materia_cambiada];

        if (select.val() != "R") {
            //tr_con_datos.removeClass(convertir_nota_materia_a_clase_tr(materia_json.nota_final));
            materia_json.nota_final = parseInt(select.val());
            //tr_con_datos.addClass(convertir_nota_materia_a_clase_tr(materia_json.nota_final));
        } else {
            //tr_con_datos.removeClass(convertir_nota_materia_a_clase_tr(materia_json.nota_final));
        }

        materia_json.esta_retirada = select.val() == "R";

        // Actualizamos los indices que se le muestran al usuario
        actualizarDatosPlanCreado();

        // Activamos el boton de guardar
        $btn_guardar_cambios.html("<i class=\"fa fa-save\"></i> Guardar Cambios*");
        $btn_guardar_cambios.removeAttr("disabled");
    }


    /**
     * Crea el Html del tr de una materia que pertenece a un trimestre
     * @param indice_trimestre indice del trimestre al que pertenece la materia
     * @param indice_materia   indice de la materia en el trimestre
     * @returns {string} Html del tr
     */
    function crearHtmlTrMateria(indice_trimestre, indice_materia) {

        var trimestre_json = modificar_plan_params.plan_creado_json.trimestres[indice_trimestre];
        var materia_json = trimestre_json.materias[indice_materia];

        // Contendrá el html del <tr></tr> resultante
        var html_tr_materia = "";

        // data-materia-codigo es para poder referenciar cual materia está en este tr
        html_tr_materia += "<tr data-materia-codigo = '" + indice_materia + "'";
        if (!materia_json.esta_retirada) {
            //html_tr_materia += " class ='" + convertir_nota_materia_a_clase_tr(materia_json.nota_final) + "'";
        }
        html_tr_materia += ">";

        // Codigo de la materia
        if (materia_json.codigo) {
            html_tr_materia += "<td>" + materia_json.codigo + "</td>";
        } else {
            html_tr_materia += "<td>Sin definir</td>";
        }

        // Nombre de la materia
        if (materia_json.nombre) {
            // El hidden-xs hace que se oculte este td en pantallas pequeñas
            html_tr_materia += "<td>" + materia_json.nombre + "</td>";
        } else {
            html_tr_materia += "<td>Sin definir</td>";
        }

        html_tr_materia += "<td >";
        html_tr_materia += convertirTipoMateriaCodigoAString(materia_json.tipo);
        html_tr_materia += "</td>";

        // Creditos de la materia
        html_tr_materia += "<td>" + materia_json.creditos + "</td>";

        // Select para las notas de la materia(Incluye la opción R - Retirada)
        html_tr_materia += "<td>";
        html_tr_materia += '<select class="selectpicker  show-tick show-menu-arrow"  title="Escoja una opción." onchange="onChangeSelectNotaFinalMateria(this)">';
        html_tr_materia += '<optgroup label="Posibles Notas">';
        for (var nota = 1; nota <= 5; nota++) {
            html_tr_materia += "<option ";
            if (materia_json.nota_final == nota) {
                html_tr_materia += "selected";
            }
            html_tr_materia += ">" + nota + "</option>";
        }
        html_tr_materia += '</optgroup>';
        html_tr_materia += '<optgroup label="¿Está retirada?">';
        html_tr_materia += ' <option title="Retirada" ';
        if (materia_json.esta_retirada) {
            html_tr_materia += "selected";
        }
        html_tr_materia += " value='R'> Retirada </option>";
        html_tr_materia += '</optgroup>';
        html_tr_materia += "</select>";
        html_tr_materia += "</td>";

        // Boton para eliminar esta materia del plan
        // Muestra un modal de confirmación

        html_tr_materia += '<td align="right" style="padding:0px;">';
        html_tr_materia += '<div class="input-group-btn">';
        html_tr_materia += '<button type="button" onclick="onClickBotonEliminarMateria(this)" class="btn btn-link" >';
        html_tr_materia += '<span class="fa fa-times" aria-hidden="true"></span>';
        html_tr_materia += '</button> ';
        html_tr_materia += '<button type="button"  data-toggle="modal" data-target="#modal-materia" data-action="editar" class="btn btn-link" >';
        html_tr_materia += '<span class="fa fa-pencil" aria-hidden="true"></span>';
        html_tr_materia += '</button> ';
        html_tr_materia += '</div>';
        html_tr_materia += "</td>";

        html_tr_materia += "</tr>";
        return html_tr_materia;
    }

    function convertirTipoMateriaCodigoAString(codigo) {

        for (var i in modificar_plan_params.tipos_materia) {
            if (modificar_plan_params.tipos_materia[i][0] == codigo) {
                return modificar_plan_params.tipos_materia[i][1]
            }
        }
        return 'Tipo desconocido - ' + codigo;
    }

    function convertirPeriodoCodigoAString(codigo) {
        switch (codigo) {
            case 'SD':
                return "Septiembre - Diciembre";
            case 'EM':
                return "Enero - Marzo";
            case 'AJ':
                return "Abril - Julio";
            case 'JA':
                return "Verano";
        }
    }

    function onClickBotonEliminarMateria(boton_jsobj) {
        var button = $(boton_jsobj);
        var tr_materia = button.closest("tr");
        var card_trimestre_jsobj = tr_materia.closest("div.card");
        var i_trimestre_materia_eliminar = parseInt(card_trimestre_jsobj.data("trimestre-codigo"));
        var j_materia_eliminar = parseInt(tr_materia.data("materia-codigo"));

        //var indices = posicion_ij_materia(i_trimestre_materia_eliminar,j_materia_eliminar);
        var trimestre_json = modificar_plan_params.plan_creado_json.trimestres[i_trimestre_materia_eliminar];
        var materia_json = trimestre_json.materias[j_materia_eliminar];

        $.confirm({
            title: 'Materia ' + convertirTipoMateriaCodigoAString(materia_json.tipo) + (materia_json.codigo ? ' ' + materia_json.codigo : ''),
            content: '¿ Eliminar ' + (materia_json.nombre ? materia_json.nombre : 'esta materia') + ' ?',
            buttons:{
                ok:{
                    text:"Sí",
                    btnClass:"btn-danger",
                    keys: ['enter'],
                    action:function () {
                        // Ocultamos el tr de la materia
                        tr_materia.hide('slow', function () {
                            tr_materia.remove();
                        });
                        // Eliminamos la materia del array
                        modificar_plan_params.plan_creado_json.trimestres[i_trimestre_materia_eliminar].materias.splice(j_materia_eliminar, 1);
                        // Actualizamos los datos del plan que se le muestran al usuario
                        actualizarDatosPlanCreado();
                        // Capacitamos al usuario para poder guardar los cambios realizados al plan
                        $btn_guardar_cambios.html("<i class=\"fa fa-save\"></i> Guardar Cambios*");
                        $btn_guardar_cambios.removeAttr("disabled");
                    }
                },
                no:{}
            },

        })
    }

    function onClickBotonEliminarTrimestre(boton_jsobj) {

        var button = $(boton_jsobj); // Button that triggered the modal
        var card_trimestre = button.closest("div.card");
        var i_trimestre = parseInt(card_trimestre.data("trimestre-codigo"));

        var trimestre_elim_json = modificar_plan_params.plan_creado_json.trimestres[i_trimestre];

        $.confirm({
            title:'Periodo: ' + convertirPeriodoCodigoAString(trimestre_elim_json.periodo) + " " + trimestre_elim_json.anyo,
            content:'¿ Eliminar el trimestre y sus materias ?',
            buttons: {
                ok:{
                    text:'Sí',
                    keys: ['enter'],
                    btnClass: 'btn-danger',
                    action:function () {
                        // Ocultamos la tabla con las materias
                        card_trimestre.hide('slow', function () {
                            card_trimestre.remove();
                        });
                        // Eliminamos el trimestre
                        modificar_plan_params.plan_creado_json.trimestres.splice(i_trimestre, 1);
                        // Actualizamos los datos del plan
                        actualizarDatosPlanCreado();
                        // Capacitamos al usuario para guardar los datos
                        $btn_guardar_cambios.html("<i class=\"fa fa-save\"></i> Guardar Cambios*");
                        $btn_guardar_cambios.removeAttr("disabled");
                    },
                },
                no:{}
            },
         });

    }


    /**
     * Crea el HTML de una tabla para un trimestre
     * @param indice_trimestre Indice del trimestre en el json al cual se le creará la tabla
     * @returns {string} HTML de la tabla -  <table></table>
     */
    function crearHtmlCardTrimestre(indice_trimestre) {

        var trimestre_json = modificar_plan_params.plan_creado_json.trimestres[indice_trimestre];

        var html_tabla_trimestre = "<div class='card card-success card-outline' data-trimestre-codigo='" + indice_trimestre + "'>";

            // HEAD de la tabla
            html_tabla_trimestre += '<div class="card-header">';
                // Periodo del trimestre
                html_tabla_trimestre += '<h3 class="card-title">';
                html_tabla_trimestre += convertirPeriodoCodigoAString(trimestre_json.periodo);
                html_tabla_trimestre += " " + trimestre_json.anyo;
                html_tabla_trimestre += "</h3>";
                // Opción de eliminar el trimestre
                html_tabla_trimestre += '<div class="card-tools pull-right">';
                    html_tabla_trimestre += '<button type="button"  data-widget="collapse" class="btn btn-tool" data-toggle="tooltip" title="Collapse">';
                        html_tabla_trimestre += '<span class="fa fa-minus"></span>';
                    html_tabla_trimestre += '</button> ';
                    html_tabla_trimestre += '<button type="button"  onclick="onClickBotonEliminarTrimestre(this)" class="btn btn-box-tool" data-toggle="tooltip" title="Remove">';
                        html_tabla_trimestre += '<span class="fa fa-times"></span>';
                    html_tabla_trimestre += '</button> ';
                html_tabla_trimestre += "</div>";
            html_tabla_trimestre += "</div>";

            // Panel Body

            html_tabla_trimestre += '<div class="card-body p-0" >';
                html_tabla_trimestre += '<table class="table table-hover">';
                    html_tabla_trimestre += "<tr>";
                    html_tabla_trimestre += "<th>Indice del Trimestre</th>";
                    html_tabla_trimestre += "<td align='center' id='td-indice-periodo-" + indice_trimestre + "' >";
                    html_tabla_trimestre += "NC";
                    html_tabla_trimestre += "</td>";
                    html_tabla_trimestre += "</tr>";
                    html_tabla_trimestre += "<tr>";
                    html_tabla_trimestre += "<th >Indice Acumulado</th>";
                    html_tabla_trimestre += "<td align='center' id='td-indice-acumulado-" + indice_trimestre + "' >";
                    html_tabla_trimestre += "NC";
                    html_tabla_trimestre += "</td>";
                    html_tabla_trimestre += "</tr>";

                html_tabla_trimestre += "</table>";

                html_tabla_trimestre += '<table class="table table-hover datos-materias-trimestre"">';

                    html_tabla_trimestre += "<thead>";
                    html_tabla_trimestre += "<tr>";
                    html_tabla_trimestre += "<th>Código</th>";
                    html_tabla_trimestre += "<th >Nombre</th>";
                    html_tabla_trimestre += "<th >Tipo</th>";
                    html_tabla_trimestre += "<th>Creditos</th>";
                    html_tabla_trimestre += "<th>Nota obtenida o ¿Retirada?</th>";
                    html_tabla_trimestre += "<th></th>";
                    html_tabla_trimestre += "</tr>";
                    html_tabla_trimestre += "</thead>";

                    html_tabla_trimestre += "<tbody  class = 'materias-trimestres'>";
                    // Creamos el html para cada tr de las materia
                    for (var indice_materia in trimestre_json.materias) {
                        html_tabla_trimestre += crearHtmlTrMateria(indice_trimestre, indice_materia)
                    }
                    html_tabla_trimestre += "</tbody>";

                html_tabla_trimestre += "</table>";

            html_tabla_trimestre += "</div>";



            html_tabla_trimestre += '<div class="card-footer">';
                html_tabla_trimestre += '<button type="button" data-toggle="modal" data-target="#modal-materia" class="btn btn-link">';
                html_tabla_trimestre += '<span class="fa fa-plus"  style="margin-left: 4px"></span>';
                html_tabla_trimestre += '</button> ';
            html_tabla_trimestre += "</div>";

        html_tabla_trimestre += "</div>";
        return html_tabla_trimestre;
    }

    actualizarDatosPlanCreado();

    $btn_float_guardar_cambios.click(function (e) {
        e.preventDefault();
        $btn_guardar_cambios.click();
    });
// Listener para cuando se clickea el boton de guardar
// El cual hace que se mande al servidor el estado del plan que maneja el cliente
// Actualizandolo
    $btn_guardar_cambios.click(function () {

        // Desactivamos los select que permiten al usuario cambiar la nota de las materias
        // Para cada select en la tabla

        $fieldset.attr("disabled", "disabled");
        $btn_float_guardar_cambios.hide(200);
        // Desactivamos el boton de guardar
        $btn_guardar_cambios.html("<i class=\"fa fa-save\"></i> Guardando Cambios...");

        // Mandamos los datos al servidor
        // Notar que mandamos un json de la forma
        // { "datos":json que el servidor nos manda}
        // Se manda de esta forma por varios errores que daba django
        var msg_actualizando_plan = alertify.notify('Actualizando <img src=' + modificar_plan_params.path_image_gear + '  style="width: 40px;height:40px;">', 'custom', 0, null);

        $.ajax({
            url: modificar_plan_params.url_api_plan_details,
            type: 'POST',
            data: JSON.stringify(modificar_plan_params.plan_creado_json),
            success: function (data, status, request) {
                alertify.success('¡Plan actualizado!');
                $btn_guardar_cambios.html("<i class=\"fa fa-save\"></i> ¡Cambios Guardados!");
                $btn_guardar_cambios.attr("disabled", "disabled")
            },
            error: function (request, status, error) {
                console.log(request, status, error);
                alertify.error('Ocurrió un error actualizando el plan :(');
                $btn_guardar_cambios.html("<i class=\"fa fa-save\"></i> Guardar Cambios*");
            },
            complete: function (request, status) {
                $fieldset.removeAttr("disabled");
                msg_actualizando_plan.dismiss();
                $btn_float_guardar_cambios.show(300);
            },
            contentType: 'application/json; indent=4;charset=UTF-8',
        });

    });

    $("a[data-accion='eliminar-plan']").click(function (e) {

        var button = $(this);
        var nombre_plan = button.data('plan-nombre');
        var id_plan = button.data('plan-id');

        $.confirm({
            title:'¿ Eliminar plan ?',
            content:'<b>Trimestres: </b> ' + modificar_plan_params.plan_creado_json.trimestres.length,
            buttons:{
                ok:{
                    text:"Sí",
                    keys: ['enter'],
                    btnClass:'btn-danger',
                    action:function(){
                        var n_puntos = 1;

                        var msg_eliminando = alertify.message('Eliminando plan.',0, function(){ clearInterval(interval);});

                         var interval = setInterval(function(){
                             n_puntos = (n_puntos + 1) % 4;
                            msg_eliminando.setContent('Eliminando plan' + ".".repeat(n_puntos));
                         },500);

                        $.ajax({
                            url:modificar_plan_params.url_api_plan_details,
                            type: 'DELETE',
                            success: function(data,status,request) {
                                alertify.success('¡Plan eliminado!');
                                msg_eliminando.dismiss();
                                setTimeout("location.reload()", 500);
                            },
                            error:function (request, status, error) {
                                msg_eliminando.dismiss();
                                console.log(status,error);
                                alertify.error('Ocurrió un error eliminando el plan')
                            },
                            contentType:'application/json; indent=4;charset=UTF-8',
                            dataType:'json',
                        });

                    }
                },
                no:{}
            },

        });
    });

    window.crearHtmlCardTrimestre = crearHtmlCardTrimestre;
    window.crearHtmlTrMateria = crearHtmlTrMateria;
    window.convertirPeriodoCodigoAString = convertirPeriodoCodigoAString;
    window.actualizarDatosPlanCreado = actualizarDatosPlanCreado;
    window.convertirTipoMateriaCodigoAString = convertirTipoMateriaCodigoAString;
    window.onClickBotonEliminarMateria = onClickBotonEliminarMateria;
    window.onClickBotonEliminarTrimestre = onClickBotonEliminarTrimestre;
    window.onChangeSelectNotaFinalMateria = onChangeSelectNotaFinalMateria;
});