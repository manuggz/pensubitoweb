/**
 * Created by manuggz on 04/03/17.
 */


// Enlaza el DOM de la tabla en la que se mostrará el plan
var div_datos_trimestres_html = $("#div-trimestres");
// Enlaza el dom del <fieldset> en el que se contienen todos los elementos con los que el usuario edita el plan
var fieldset = $("fieldset");
// Enlaza el DOM del boton que se presiona para actualizar los datos del plan del servidor
var btn_guardar_cambios = $("#btn-guardar-cambios");


/**
 * Redondea un numero ejem: 123.123453 a 4 cífras significativas a lo más. ejem: 123.1235
 * @param numero
 * @returns {number}
 */
function redondear(numero){
    return Math.round((numero + 0.00001)*10000)/10000;
}


// Actualiza los indices(indice periodo e Indice acumulado) que se le muestra al usuario
// Básicamente recorre el JSON(plan_creado_json) donde se guardan los datos de los trimestres
// A medida que lo va recorriendo va calculando y actualizando los datos que se le muestran al usuario
function actualizar_datos_plan_creado(){
    // Nota: Recordar que el índice se calcula
    // sumatoria(nota(i)*creditomateria(i)) / sumatoria(creditosdemateria(i))
    // Si el estudiante pasa(nota >= 3) una materia previamente reprobada se anula la nota inmediata anterior

    // Contendrá la suma parcial nota(i)*creditomateria(i)
    var sum_nota_creds_acum   = 0;

    // Total de creditos inscritos por el usuario
    // contiene creditos retirados,aprobados,reprobados
    var creds_inscri = 0;
    // Total de creditos retirados
    // Creditos inscritos que el estudiante retiró
    var creds_ret = 0;
    // Total de creditos aprobados
    // Creditos que el estudiante inscribió y aprobó con una nota mayor o igual a 3
    var creds_apro = 0;
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
    // Recorremos todos los trimestres
    // i tomará valores desde 0 hasta total(trimestres cursados)
    for(var i in plan_creado_json.trimestres) {
        // Suma de nota(i)*creditosmateria(i) del trimestre actual del bucle
        // Se usa para calcular el indice del periodo/trimestre actual
        var sum_nota_creds_trimact = 0;
        // Total de los creditos que cuentan para el trimestre actual
        var cred_cont_trimact = 0;
        var trimestre_json = plan_creado_json.trimestres[i];

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
                        for (var m in plan_creado_json.trimestres[l].materias) {
                            // Si es la misma materia (comparamos el código)
                            if (plan_creado_json.trimestres[l].materias[m].codigo == materia_planeada.codigo) {

                                // Si la materia está reprobada y no está retirada
                                // Significa que debemos anular esta nota
                                if (plan_creado_json.trimestres[l].materias[m].nota_final <= 2 && !plan_creado_json.trimestres[l].materias[m].esta_retirada) {
                                    nota_reprobada_anterior = plan_creado_json.trimestres[l].materias[m].nota_final;
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
                }

                // Aumentamos la suma nota i x credito materia i
                sum_nota_creds_trimact += materia_planeada.nota_final * cred_trim_actual;
                // Aumentamos la suma de creditos para este trimestre
                cred_cont_trimact += cred_trim_actual;

            } else {
                // Aumentamos los creditos retirados
                creds_ret += cred_trim_actual;
            }
        }

        // Aumentamos la suma nota i * credito i para el acumulado
        sum_nota_creds_acum += sum_nota_creds_trimact;
        // Aumentamos la suma de creditos que cuentan totales
        creds_cont += cred_cont_trimact;
        // Actualizamos lo que se le muestra al usuario
        // Notar que se ha usado la notación #td-indice-<codigo trimestre> para referenciar el td que muestra
        // los datos para el trimestre <código trimestre>

        if (isNaN(sum_nota_creds_trimact)){
            div_datos_trimestres_html.find("#td-indice-periodo-" + i).html("<abbr title='Nota no calculable'>N.C.</abbr>");
        }else{
            div_datos_trimestres_html.find("#td-indice-periodo-" + i).html(
                redondear(sum_nota_creds_trimact   / cred_cont_trimact)
            );
        }

        if (isNaN(sum_nota_creds_acum)){
            div_datos_trimestres_html.find("#td-indice-acumulado-" + i).html("<abbr title='Nota no calculable'>N.C.</abbr>");
        }else {

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
                html_indice_acumulado += "<img src='" + path_image_flecha_same + "' style='width:15px;height:15px;'/>"
            } else if (indice_acumulado_actual > indice_acumulado_anterior) {
                html_indice_acumulado += "<img src='" + path_image_flecha_up + "' style='width:15px;height:15px;'/>";
                html_indice_acumulado += "( +" + redondear(diferencia) + ")"
            } else {
                html_indice_acumulado += "<img src='" + path_image_flecha_down + "' style='width:15px;height:15px;'/>";
                html_indice_acumulado += "( -" + redondear(diferencia) + ")"
            }


            div_datos_trimestres_html.find("#td-indice-acumulado-" + i).html(html_indice_acumulado);

            indice_acumulado_anterior = indice_acumulado_actual;
        }
    }
}

/**
 * Callback para cuando se cambia la nota de una materia en la tabla
 * @param sel_obj Objeto al cual se le cambio la nota (this = select javascript)
 */
function on_change_select_nota_final(sel_obj){
    // Se ha hecho tal que en los tr del tbody de la tabla
    // se guarden datos usables para el código
    // por lo que lo primero es encontrar el más cernano tr del elemento
    var select = $(sel_obj);
    var tr_con_datos = select.closest( "tr" );
    var panel_con_datos = tr_con_datos.closest( "div.panel" );

    // Obtenemos los datos de la materia y trimestre a la cual pertenece
    var i_trimestre_cambiado = parseInt(panel_con_datos.data("trimestre-codigo"));
    var j_materia_cambiada   = parseInt(tr_con_datos.data("materia-codigo"));

    //var posicion_materia = posicion_ij_materia(i_trimestre_cambiado,j_materia_cambiada);
    var trimestre_json = plan_creado_json.trimestres[i_trimestre_cambiado];
    var materia_json = trimestre_json.materias[j_materia_cambiada];

    if(select.val() != "R"){
        //tr_con_datos.removeClass(convertir_nota_materia_a_clase_tr(materia_json.nota_final));
        materia_json.nota_final = parseInt(select.val());
        //tr_con_datos.addClass(convertir_nota_materia_a_clase_tr(materia_json.nota_final));
    }else{
        //tr_con_datos.removeClass(convertir_nota_materia_a_clase_tr(materia_json.nota_final));
    }

    materia_json.esta_retirada = select.val() == "R";

    // Actualizamos los indices que se le muestran al usuario
    actualizar_datos_plan_creado();

    // Activamos el boton de guardar
    btn_guardar_cambios.text("Guardar Cambios*");
    btn_guardar_cambios.removeAttr("disabled");
}


/**
 * Crea el Html del tr de una materia que pertenece a un trimestre
 * @param indice_trimestre indice del trimestre al que pertenece la materia
 * @param indice_materia   indice de la materia en el trimestre
 * @returns {string} Html del tr
 */
function crear_html_tr_materia(indice_trimestre,indice_materia){

    var trimestre_json = plan_creado_json.trimestres[indice_trimestre];
    var materia_json = trimestre_json.materias[indice_materia];

    // Contendrá el html del <tr></tr> resultante
    var html_tr_materia = "";

    // data-materia-codigo es para poder referenciar cual materia está en este tr
    html_tr_materia += "<tr data-materia-codigo = '" + indice_materia + "'";
    if(!materia_json.esta_retirada) {
        //html_tr_materia += " class ='" + convertir_nota_materia_a_clase_tr(materia_json.nota_final) + "'";
    }
    html_tr_materia += ">";

        // Codigo de la materia
        if(materia_json.codigo){
            html_tr_materia += "<td>" + materia_json.codigo + "</td>";
        }else{
            html_tr_materia += "<td><abbr title='Sin Definir '>Sin.Defi.</abbr> </td>";
        }

        // Nombre de la materia
        if(materia_json.nombre){
            // El hidden-xs hace que se oculte este td en pantallas pequeñas
            html_tr_materia += "<td>" + materia_json.nombre + "</td>";
        }else{
            html_tr_materia += "<td><abbr title='Sin Definir '>Sin.Defi.</abbr> </td>";
        }

       html_tr_materia += "<td >";
            html_tr_materia += convertir_tipo_materia_codigo_a_string(materia_json.tipo);
        html_tr_materia += "</td>";

        // Creditos de la materia
        html_tr_materia += "<td>" + materia_json.creditos + "</td>";

        // Select para las notas de la materia(Incluye la opción R - Retirada)
        html_tr_materia += "<td>";
            html_tr_materia += '<select class="selectpicker  show-tick show-menu-arrow"  title="Escoja una opción." onchange="on_change_select_nota_final(this)">';
                html_tr_materia+='<optgroup label="Posibles Notas">';
                    for (var nota = 1; nota <= 5; nota++) {
                        html_tr_materia += "<option ";
                        if(materia_json.nota_final == nota){
                            html_tr_materia+="selected";
                        }
                        html_tr_materia += ">" + nota + "</option>";
                    }
                html_tr_materia+='</optgroup>';
                html_tr_materia+='<optgroup label="¿Está retirada?">';
                    html_tr_materia += ' <option title="Retirada" ';
                    if(materia_json.esta_retirada){
                        html_tr_materia+="selected";
                    }
                    html_tr_materia += " value='R'> Retirada </option>";
                html_tr_materia+='</optgroup>';
            html_tr_materia += "</select>";
        html_tr_materia += "</td>";

        // Boton para eliminar esta materia del plan
        // Muestra un modal de confirmación

        html_tr_materia += '<td align="right" style="padding:0px;">';
            html_tr_materia += '<div class="input-group-btn">';
                html_tr_materia += '<button type="button" onclick="on_click_boton_eliminar_materia(this)" class="btn btn-link" >';
                    html_tr_materia += '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>';
                html_tr_materia += '</button> ';
                html_tr_materia += '<button type="button"  data-toggle="modal" data-target="#modal-materia" data-action="editar" class="btn btn-link" >';
                    html_tr_materia += '<span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>';
                html_tr_materia += '</button> ';
            html_tr_materia += '</div>';
        html_tr_materia += "</td>";

    html_tr_materia += "</tr>";
    return html_tr_materia;
}
function convertir_tipo_materia_codigo_a_string(codigo) {

    for(var i in tipos_materia){
        if(tipos_materia[i][0] == codigo){
            return tipos_materia[i][1]
        }
    }
    return 'Tipo desconocido - ' + codigo;
}
function convertir_periodo_codigo_a_string(codigo) {
    switch(codigo){
        case 'SD':
            return "Septiembre - Diciembre";
        case 'EM':
            return "Enero - Marzo";
        case 'AJ':
            return "Abril - Julio";
        case 'JA':
            return "Julio - Agosto";
    }
}

function on_click_boton_eliminar_materia(boton_jsobj) {
    var button = $(boton_jsobj);
    var tr_materia =  button.closest( "tr" );
    var panel_trimestre_jsobj = tr_materia.closest( "div.panel" );
    var i_trimestre_materia_eliminar = parseInt(panel_trimestre_jsobj.data("trimestre-codigo"));
    var j_materia_eliminar   = parseInt(tr_materia.data("materia-codigo"));

    //var indices = posicion_ij_materia(i_trimestre_materia_eliminar,j_materia_eliminar);
    var trimestre_json = plan_creado_json.trimestres[i_trimestre_materia_eliminar];
    var materia_json = trimestre_json.materias[j_materia_eliminar];

    alertify.confirm(
        'Materia: ' +  materia_json.codigo,
        '¿ Eliminar : "' + materia_json.nombre + '" ?',
        function(){
            // Ocultamos el tr de la materia
            tr_materia.hide('slow', function(){ tr_materia.remove(); });
            // Eliminamos la materia del array
            plan_creado_json.trimestres[i_trimestre_materia_eliminar].materias.splice(j_materia_eliminar,1);
            // Actualizamos los datos del plan que se le muestran al usuario
            actualizar_datos_plan_creado();
            // Capacitamos al usuario para poder guardar los cambios realizados al plan
            btn_guardar_cambios.text("Guardar Cambios*");
            btn_guardar_cambios.removeAttr("disabled");
        },
        null
    ).setting({
        'labels':{ok:'¡Sí!', cancel:'¡No!'}
    });
}

function on_click_boton_eliminar_trimestre(boton_jsobj) {
    var button = $(boton_jsobj); // Button that triggered the modal
    var panel_trimestre = button.closest( "div.panel" );
    var i_trimestre = parseInt(panel_trimestre.data("trimestre-codigo"));

    var trimestre_elim_json = plan_creado_json.trimestres[i_trimestre];

    alertify.confirm(
        'Periodo: ' +  convertir_periodo_codigo_a_string(trimestre_elim_json.periodo) + " " + trimestre_elim_json.anyo,
        '¿ Eliminar el trimestre y sus materias ?',
        function(){
            // Ocultamos la tabla con las materias
            panel_trimestre.hide('slow', function(){ panel_trimestre.remove(); });
            // Eliminamos el trimestre
            plan_creado_json.trimestres.splice(i_trimestre,1);
            // Actualizamos los datos del plan
            actualizar_datos_plan_creado();
            // Capacitamos al usuario para guardar los datos
            btn_guardar_cambios.text("Guardar Cambios*");
            btn_guardar_cambios.removeAttr("disabled");
        },
        null
    ).setting({
        'labels':{ok:'¡Sí!', cancel:'¡No!'}
    });

}



/**
 * Crea el HTML de una tabla para un trimestre
 * @param indice_trimestre Indice del trimestre en el json al cual se le creará la tabla
 * @returns {string} HTML de la tabla -  <table></table>
 */
function crear_html_panel_trimestre(indice_trimestre){

    var trimestre_json =  plan_creado_json.trimestres[indice_trimestre];

    var html_tabla_trimestre = "<div class='panel panel-success' data-trimestre-codigo='" + indice_trimestre +  "'>";

        // HEAD de la tabla
        html_tabla_trimestre+= '<div class="panel-heading" style="padding: 0px;">';
            html_tabla_trimestre += '<div class="input-group">';
                // Periodo del trimestre
                html_tabla_trimestre += '<h3 class="panel-title" style="padding-top: 9px;padding-left: 9px;">';
                    html_tabla_trimestre += convertir_periodo_codigo_a_string(trimestre_json.periodo);
                    html_tabla_trimestre += " " + trimestre_json.anyo;
                html_tabla_trimestre += "</h3>";
                // Opción de eliminar el trimestre
                html_tabla_trimestre += '<div class="input-group-btn">';
                    html_tabla_trimestre += '<button type="button" onclick="on_click_boton_eliminar_trimestre(this)" class="btn btn-link">';
                        html_tabla_trimestre += '<span class="glyphicon glyphicon-trash"></span>';
                    html_tabla_trimestre += '</button> ';
                html_tabla_trimestre += "</div>";
            html_tabla_trimestre += "</div>";
        html_tabla_trimestre += "</div>";

        // Panel Body

        html_tabla_trimestre += '<div class="panel-body" style="padding: 0px;">';
            html_tabla_trimestre += '<table class="table table-hover datos-trimestre">';
                    html_tabla_trimestre += "<tr>";
                        html_tabla_trimestre += "<th>Indice del Trimestre</th>";
                        html_tabla_trimestre += "<td align='center' id='td-indice-periodo-"  + trimestre_json.codigo + "' >";
                            html_tabla_trimestre += "NC";
                        html_tabla_trimestre += "</td>";
                    html_tabla_trimestre += "</tr>";
                    html_tabla_trimestre += "<tr>";
                        html_tabla_trimestre += "<th >Indice Acumulado</th>";
                        html_tabla_trimestre += "<td align='center' id='td-indice-acumulado-"  + trimestre_json.codigo + "' >";
                            html_tabla_trimestre += "NC";
                        html_tabla_trimestre += "</td>";
                    html_tabla_trimestre += "</tr>";

            html_tabla_trimestre += "</table>";
        html_tabla_trimestre += "</div>";

        html_tabla_trimestre += '<table class="table table-hover datos-trimestre"">';

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
                for(var  indice_materia in trimestre_json.materias){
                    html_tabla_trimestre += crear_html_tr_materia(indice_trimestre,indice_materia)
                }
            html_tabla_trimestre += "</tbody>";

        html_tabla_trimestre += "</table>";

        html_tabla_trimestre += '<div class="panel-footer">';
            html_tabla_trimestre += '<button type="button" data-toggle="modal" data-target="#modal-materia"class="btn btn-link">';
                html_tabla_trimestre += '<span class="glyphicon glyphicon-plus"  style="margin-left: 4px"></span>';
            html_tabla_trimestre += '</button> ';
        html_tabla_trimestre += "</div>";

    html_tabla_trimestre += "</div>";
    return html_tabla_trimestre;
}
