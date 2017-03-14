/**
 * Created by manuggz on 04/03/17.
 */

// Enlaza el DOM de la tabla en la que se mostrará el plan
var div_datos_trimestres_html      =  $("#div-trimestres");;

// Enlaza el dom del <fieldset> en el que se contienen todos los elementos con los que el usuario edita el plan
var fieldset = $("fieldset");
// Enlaza el DOM del boton que se presiona para actualizar los datos del plan del servidor
var btn_guardar_cambios   =  $("#btn-guardar-cambios");;
// Contiene el json que manda el servidor que contiene el plan
// Se utiliza así mismo para controlar los datos del plan del cliente
// Si se agrega/elimina-modifica algo del plan se debe reflejar aquí
// ya que este es el que se envía al servidor para que se actualize los datos que el
// servidor contiene
var plan_creado_json = null;
// Variable usada para asignarles codigos a los trimestres distintos de los manejados por el servidor
// Esto sirve por si se quiere modificar/eliminar un trimestre en particular para diferenciarlo
// -- Contiene el código que se le asignará al siguiente trimestre a registrar
var next_cod_trime = 0;

var boton_agregar_trim = null;

// Redondea un numero ejem: 123.123453 a 4 cífras significativas a lo más. ejem: 123.1235
function redondear(numero){
    return Math.round((numero + 0.00001)*10000)/10000;
}

// Busca la posicion de la materia con el código codigo_materia que pertenece
// al trimestre con el código codigo_trimestre
// regresa la posición i,j
// i - posición del trimestre en el array de trimestres del JSON plan_creado_json
// j - posición de la materia en el array de materias del trimestre i
function posicion_ij_materia(codigo_trimestre, codigo_materia) {
    for(var i in plan_creado_json.trimestres_planeados){
        if(plan_creado_json.trimestres_planeados[i].codigo == codigo_trimestre){
            for(var j in plan_creado_json.trimestres_planeados[i].materias_planeadas){
                if(plan_creado_json.trimestres_planeados[i].materias_planeadas[j].codigo == codigo_materia) {
                    return [i,j]
                }
            }
        }
    }
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
    for(var i in plan_creado_json.trimestres_planeados) {
        // Suma de nota(i)*creditosmateria(i) del trimestre actual del bucle
        // Se usa para calcular el indice del periodo/trimestre actual
        var sum_nota_creds_trimact = 0;
        // Total de los creditos que cuentan para el trimestre actual
        var cred_cont_trimact = 0;
        var trimestre_json = plan_creado_json.trimestres_planeados[i];

        // Recorremos todas las materias inscritas para el trimestre i
        for (var j in trimestre_json.materias_planeadas) {

            var materia_planeada = trimestre_json.materias_planeadas[j];

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
                        for (var m in plan_creado_json.trimestres_planeados[l].materias_planeadas) {
                            // Si es la misma materia (comparamos el código)
                            if (plan_creado_json.trimestres_planeados[l].materias_planeadas[m].codigo == materia_planeada.codigo) {

                                // Si la materia está reprobada y no está retirada
                                // Significa que debemos anular esta nota
                                if (plan_creado_json.trimestres_planeados[l].materias_planeadas[m].nota_final <= 2 && !plan_creado_json.trimestres_planeados[l].materias_planeadas[m].esta_retirada) {
                                    nota_reprobada_anterior = plan_creado_json.trimestres_planeados[l].materias_planeadas[m].nota_final;
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
        div_datos_trimestres_html.find("#td-indice-periodo-" + trimestre_json.codigo).html(
            redondear(sum_nota_creds_trimact   / cred_cont_trimact)
        );

        indice_acumulado_actual = redondear(sum_nota_creds_acum   / creds_cont);

        var html_indice_acumulado = "";
        if(indice_acumulado_actual > 4.0) {
            html_indice_acumulado += "<strong style='color: green;'>" + indice_acumulado_actual + "</strong>"
        }else if(indice_acumulado_actual < 2.9){
            html_indice_acumulado += "<strong style='color: red;'>" + indice_acumulado_actual + "</strong>"
        }else{
            html_indice_acumulado += indice_acumulado_actual
        }

        var diferencia = Math.abs(indice_acumulado_actual - indice_acumulado_anterior);
        if( diferencia < 0.0001){
            html_indice_acumulado += "<img src='" + path_image_flecha_same + "' style='width:15px;heigh:15px;'/>"
        }else if(indice_acumulado_actual > indice_acumulado_anterior){
            html_indice_acumulado += "<img src='" + path_image_flecha_up + "' style='width:15px;heigh:15px;'/>"
            html_indice_acumulado += "( +" + redondear(diferencia)+ ")"
        }else{
            html_indice_acumulado += "<img src='" + path_image_flecha_down + "' style='width:15px;heigh:15px;'/>"
            html_indice_acumulado += "( -" + redondear(diferencia) + ")"
        }


        div_datos_trimestres_html.find("#td-indice-acumulado-" + trimestre_json.codigo).html(html_indice_acumulado)
        indice_acumulado_anterior = indice_acumulado_actual;
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
    var table_con_datos = tr_con_datos.closest( "table" );

    // Obtenemos los datos de la materia y trimestre a la cual pertenece
    var codigo_trimestre_cambiado = table_con_datos.data("trimestre-codigo");
    var codigo_materia_cambiada   = tr_con_datos.data("materia-codigo");

    var posicion_materia = posicion_ij_materia(codigo_trimestre_cambiado,codigo_materia_cambiada);
    var trimestre_json = plan_creado_json.trimestres_planeados[posicion_materia[0]];
    var materia_json = trimestre_json.materias_planeadas[posicion_materia[1]];

    if(select.val() != "R"){
        tr_con_datos.removeClass(convertir_nota_materia_a_clase_tr(materia_json.nota_final));
        materia_json.nota_final = parseInt(select.val());
        tr_con_datos.addClass(convertir_nota_materia_a_clase_tr(materia_json.nota_final));
    }else{
        tr_con_datos.removeClass(convertir_nota_materia_a_clase_tr(materia_json.nota_final));
    }

    materia_json.esta_retirada = select.val() == "R";

    // Actualizamos los indices que se le muestran al usuario
    actualizar_datos_plan_creado();

    // Activamos el boton de guardar
    btn_guardar_cambios.text("Guardar Cambios*");
    btn_guardar_cambios.removeAttr("disabled");
}


// Listener para cuando se clickea el boton de guardar
// El cual hace que se mande al servidor el estado del plan que maneja el cliente
// Actualizandolo
btn_guardar_cambios.click(function () {

    // Desactivamos los select que permiten al usuario cambiar la nota de las materias
    // Para cada select en la tabla

    fieldset.attr("disabled","disabled");

    // Desactivamos el boton de guardar
    btn_guardar_cambios.text("Guardando Cambios...");

    // Mandamos los datos al servidor
    // Notar que mandamos un json de la forma
    // { "datos":json que el servidor nos manda}
    // Se manda de esta forma por varios errores que daba django
    var msg_actualizando_plan = alertify.notify('Actualizando <img src=' + path_image_gear + '  style="width: 40px;height:40px;">','custom',0,null);

    $.ajax({
        url:location.origin + "/api/planes_creados/" + plan_creado_json.id + "/",
        type: 'PUT',
        data:JSON.stringify(plan_creado_json),
        success: function(data,status,request) {
            alertify.success('¡Plan actualizado!');
            btn_guardar_cambios.text("¡Cambios Guardados!");
            btn_guardar_cambios.attr("disabled","disabled")
        },
        error:function (request, status, error) {
            console.log(status,error);
            alertify.error('Ocurrió un error actualizando el plan :(')
            btn_guardar_cambios.text("Guardar Cambios*");
        },
        complete:function (request,status) {
            fieldset.removeAttr("disabled");
            msg_actualizando_plan.dismiss();
        },
        contentType:'application/json; indent=4;charset=UTF-8',
    });

});

/**
 * Crea el Html del tr de una materia que pertenece a un trimestre
 * @param indice_trimestre indice del trimestre al que pertenece la materia
 * @param indice_materia   indice de la materia en el trimestre
 * @returns {string} Html del tr
 */
function crear_html_tr_materia(indice_trimestre,indice_materia){

    var trimestre_json = plan_creado_json.trimestres_planeados[indice_trimestre];
    var materia_json = trimestre_json.materias_planeadas[indice_materia];

    // Contendrá el html del <tr></tr> resultante
    var html_tr_materia = "";

    // data-materia-codigo es para poder referenciar cual materia está en este tr
    html_tr_materia += "<tr data-materia-codigo = '" + materia_json.codigo + "'";
    if(!materia_json.esta_retirada) {
        html_tr_materia += " class ='" + convertir_nota_materia_a_clase_tr(materia_json.nota_final) + "'";
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
            html_tr_materia += "<td  class = 'hidden-xs'>" + materia_json.nombre + "</td>";
        }else{
            html_tr_materia += "<td  class = 'hidden-xs'>";
                html_tr_materia += convertir_tipo_materia_codigo_a_string(materia_json.tipo);
            html_tr_materia += "</td>";
        }

        // Creditos de la materia
        html_tr_materia += "<td>" + materia_json.creditos + "</td>";

        // Select para las notas de la materia(Incluye la opción R - Retirada)
        html_tr_materia += "<td>";
            html_tr_materia += "<select class='form-control' onchange='on_change_select_nota_final(this)'>";
                for (var nota = 1; nota <= 5; nota++) {
                    html_tr_materia += "<option ";
                    if(materia_json.nota_final == nota){
                        html_tr_materia+="selected";
                    }
                    html_tr_materia += ">" + nota + "</option>";
                }
                html_tr_materia += "<option ";
                if(materia_json.esta_retirada){
                    html_tr_materia+="selected";
                }
                html_tr_materia += ">R</option>";
            html_tr_materia += "</select>";
        html_tr_materia += "</td>";

        // Boton para eliminar esta materia del plan
        // Muestra un modal de confirmación
        html_tr_materia += "<td>";
            html_tr_materia += '<button type="button" onclick="on_click_boton_eliminar_materia(this)" class="btn btn-warning" >';
                html_tr_materia += '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span>';
            html_tr_materia += '</button> ';
        html_tr_materia += "</td>";

    html_tr_materia += "</tr>";
    return html_tr_materia;
}
function convertir_nota_materia_a_clase_tr(nota) {
    switch(nota){
        case 5:
            return 'success';
        case 4:
        case 3:
            return 'active';
        case 2:
            return 'warning';
        case 1:
            return 'danger';
    }

}
function convertir_tipo_materia_codigo_a_string(codigo) {
    switch(codigo){
        case 'RG':
            return  "Materia Regular";
        case 'GE':
            return  "General";
        case 'EA':
            return  "Electiva de Area";
        case 'EL':
            return  "Electiva Libre";
        case 'PC':
            return  "Pasantia Corta";
        case 'PL':
            return  "Pasantia Larga";
        case 'EX':
            return  "Extraplan";
        default:
            return 'Tipo desconocido - ' + codigo;
    }
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
    var table_trimestre = tr_materia.closest( "table" );
    var codigo_trimestre_materia_eliminar = table_trimestre.data("trimestre-codigo");
    var codigo_materia_eliminar   = tr_materia.data("materia-codigo");

    var indices = posicion_ij_materia(codigo_trimestre_materia_eliminar,codigo_materia_eliminar);
    var trimestre_json = plan_creado_json.trimestres_planeados[indices[0]];
    var materia_json = trimestre_json.materias_planeadas[indices[1]];

    alertify.confirm(
        'Materia: ' +  materia_json.codigo,
        '¿ Eliminar : "' + materia_json.nombre + '" ?',
        function(){
            // Ocultamos el tr de la materia
            tr_materia.hide('slow', function(){ tr_materia.remove(); });
            // Eliminamos la materia del array
            plan_creado_json.trimestres_planeados[indices[0]].materias_planeadas.splice(indices[1],1);
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
    var tr_materia =  button.closest( "tr" );
    var table_trimestre = tr_materia.closest( "table" );
    var codigo_trimestre_materia_eliminar = table_trimestre.data("trimestre-codigo");

    var indice_tratado = -1;
    for(var indice_trimestre in plan_creado_json.trimestres_planeados){
        if(plan_creado_json.trimestres_planeados[indice_trimestre].codigo == codigo_trimestre_materia_eliminar){
            indice_tratado = indice_trimestre;
            break;
        }
    }
    if(indice_trimestre == -1) return;

    var trimestre_elim_json = plan_creado_json.trimestres_planeados[indice_tratado];

    alertify.confirm(
        'Periodo: ' +  convertir_periodo_codigo_a_string(trimestre_elim_json.periodo) + " " + trimestre_elim_json.anyo,
        '¿ Eliminar el trimestre y sus materias ?',
        function(){
            // Ocultamos la tabla con las materias
            table_trimestre.hide('slow', function(){ table_trimestre.remove(); });
            // Eliminamos el trimestre
            plan_creado_json.trimestres_planeados.splice(indice_tratado,1);
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
function crear_html_tabla_trimestre(indice_trimestre){

    var trimestre_json =  plan_creado_json.trimestres_planeados[indice_trimestre];

    var html_tabla_trimestre = "<table class='table' data-trimestre-codigo='" + trimestre_json.codigo +  "'>";
        // HEAD de la tabla
        html_tabla_trimestre+= "<thead>";
            html_tabla_trimestre += "<tr>";
                // Periodo del trimestre
                html_tabla_trimestre += "<th colspan='3'>";
                    html_tabla_trimestre += convertir_periodo_codigo_a_string(trimestre_json.periodo);
                    html_tabla_trimestre += " " + trimestre_json.anyo;
                html_tabla_trimestre += "</th>";
                // Opción de eliminar el trimestre
                html_tabla_trimestre += "<th colspan='2' align='right'>";
                    html_tabla_trimestre += '<button type="button" onclick="on_click_boton_eliminar_trimestre(this)" class="btn btn-danger">';
                        html_tabla_trimestre += '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span>';
                        html_tabla_trimestre += '¡Eliminar trimestre!';
                    html_tabla_trimestre += '</button> ';
                html_tabla_trimestre += "</th>"; // Falta identificador de indice/materia
            html_tabla_trimestre += "</tr>"; // Falta identificador de indice/materia
        html_tabla_trimestre += "</thead>"; // Falta identificador de indice/materia

        // Body
        html_tabla_trimestre += "<tbody>";
            html_tabla_trimestre += "<tr>";
                html_tabla_trimestre += "<th>Código</th>";
                html_tabla_trimestre += "<th class = 'hidden-xs'>Nombre/Tipo</th>";
                html_tabla_trimestre += "<th>Creditos</th>";
                html_tabla_trimestre += "<th>Nota</th>";
                html_tabla_trimestre += "<th>¿Eliminar?</th>";
            html_tabla_trimestre += "</tr>";

        // Creamos el html para cada tr de las materia
        for(var  indice_materia in trimestre_json.materias_planeadas){
            html_tabla_trimestre += crear_html_tr_materia(indice_trimestre,indice_materia)
        }

        html_tabla_trimestre += "<tr>";
            html_tabla_trimestre += "<td colspan='5' align='center'>";
                html_tabla_trimestre += '<button type="button" data-toggle="modal" data-target="#modal-agregar-mat" class="btn btn-primary" >';
                    html_tabla_trimestre += '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span>';
                    html_tabla_trimestre += '¡Agregar Materia!';
                html_tabla_trimestre += '</button> ';
            html_tabla_trimestre += "</td>";
        html_tabla_trimestre += "</tr>";

        html_tabla_trimestre += "</tbody>";
        html_tabla_trimestre += "<tfoot>";
            html_tabla_trimestre += "<tr>";
                html_tabla_trimestre += "<td align='center'>";
                    html_tabla_trimestre += "<strong>Indice.Periodo.:</strong>"
                html_tabla_trimestre += "</td>";
                html_tabla_trimestre += "<td align='left' id='td-indice-periodo-"  + trimestre_json.codigo + "' >";
                    html_tabla_trimestre += "NC";
                html_tabla_trimestre += "</td>";
                html_tabla_trimestre += "<td align='center' >";
                    html_tabla_trimestre += "<strong>Indice.Acumulado.:</strong>";
                html_tabla_trimestre += "</td>";
                html_tabla_trimestre += "<td align='left' id='td-indice-acumulado-"  + trimestre_json.codigo + "' >";
                    html_tabla_trimestre += "NC";
                html_tabla_trimestre += "</td>";
            html_tabla_trimestre += "</tr>";
        html_tabla_trimestre += "</tfoot>";
    html_tabla_trimestre += "</table>";
    return html_tabla_trimestre;
}

/**
 * Crea el HTML del boton agregar trimestre
 */

/**
 * Crea las tablas de los trimestres, se llama al inicio cuando se carga la página
 */
function crear_tabla_trimestres(){
    var html_tablas_trim = "";

    for(var indice_trimestre in plan_creado_json.trimestres_planeados){
        plan_creado_json.trimestres_planeados[indice_trimestre].codigo = next_cod_trime++;
        html_tablas_trim += crear_html_tabla_trimestre(indice_trimestre);
    }

    div_datos_trimestres_html.html(html_tablas_trim);
    boton_agregar_trim = $('<div style="width:185px;margin:auto;" ><button  type="button" data-toggle="modal" data-target="#modal-agregar-trim"  class="btn btn-primary"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> ¡Agregar Trimestre!</button></div>');
    div_datos_trimestres_html.append(boton_agregar_trim)
}


/************************ Codigo para el modal agregar materia ***********************+*/

var modal_agregar_mat = $("#modal-agregar-mat");
var  select_creditos_en_modal = modal_agregar_mat.find("#id_select_cred");
var  txt_input_codigo_mat_en_modal = modal_agregar_mat.find("#id_txt_input_codigo_mat");
var  txt_input_nombre_mat_en_modal = modal_agregar_mat.find("#id_txt_input_nombre_mat");
var  select_tipo_mat_en_modal = modal_agregar_mat.find("#id_select_tipo_materia");

var dowpdown_opciones_codigos = $("datalist[id='codigos']");
var dowpdown_opciones_materias_nombres = $("datalist[id='nombres_mat']");

var btn_agregar_mat_en_modal = modal_agregar_mat.find("#btn-agregar-mat");
var indice_tratado = -1;
var button_related ;

modal_agregar_mat.on('show.bs.modal', function (event) {
    button_related = $(event.relatedTarget);
    var table_trimestre =  button_related.closest( "table" );
    var codigo_trimestre   = table_trimestre.data("trimestre-codigo");

    for (var i in plan_creado_json.trimestres_planeados){
        if(codigo_trimestre == plan_creado_json.trimestres_planeados[i].codigo){
            indice_tratado = i;
            break;
        }
    }
});

btn_agregar_mat_en_modal.click(function (event) {

    modal_agregar_mat.modal("hide");
    var nueva_mat_json = {
        'codigo':txt_input_codigo_mat_en_modal.val(),
        'nombre':txt_input_nombre_mat_en_modal.val(),
        'creditos':parseInt(select_creditos_en_modal.val()),
        'nota_final':parseInt(modal_agregar_mat.find("#id_select_nota_final").val()),
        'esta_retirada':modal_agregar_mat.find("#id_check_esta_retirada")[0].checked,
        'tipo':select_tipo_mat_en_modal.val(),
    };

    var n_materias = plan_creado_json.trimestres_planeados[indice_tratado].materias_planeadas.length;
    plan_creado_json.trimestres_planeados[indice_tratado].materias_planeadas[n_materias] = nueva_mat_json;

    var nuevo_tr_mat_jquer = $(crear_html_tr_materia(indice_tratado,n_materias)).hide();

    // PAra insertarlo antes del boton
    nuevo_tr_mat_jquer.insertBefore(button_related.closest("tr"));

    nuevo_tr_mat_jquer.show('slow');

    actualizar_datos_plan_creado();
    btn_guardar_cambios.text("Guardar Cambios*");
    btn_guardar_cambios.removeAttr("disabled");

});


txt_input_codigo_mat_en_modal.on('input',function(e){
    $.get("{% url 'materias' %}",{
                codigo:txt_input_codigo_mat_en_modal.val(),
                max_length:5,
            },
            function(data, status){
                if (status == "success"){
                    console.log(data)
                    if(data.materias.length == 1 && data.materias[0].codigo == txt_input_codigo_mat_en_modal.val()){
                        select_creditos_en_modal.val(data.materias[0].creditos);
                        txt_input_nombre_mat_en_modal.val(data.materias[0].nombre);
                    }else{
                        var html_dropdown = '';
                        for(var i in data.materias){
                            html_dropdown += '<option value="' + data.materias[i].codigo + '">' + data.materias[i].codigo+" - " +data.materias[i].nombre+ '</option>';

                        }
                        dowpdown_opciones_codigos.html(html_dropdown);
                    }
                }else{
                    console.log("Ocurrió un error obteniendo materias");
                }
        }
    );
});
txt_input_nombre_mat_en_modal.on('input',function(e){
    $.get(location.origin + "/api/users/" + "11-10390"  +  "/planes/",{
                nombre:txt_input_nombre_mat_en_modal.val(),
                max_length:5,
            },
            function(data, status){
                if (status == "success"){
                    if(data.materias.length == 1 && data.materias[0].nombre == txt_input_nombre_mat_en_modal.val()){
                        select_creditos_en_modal.val(data.materias[0].creditos);
                        txt_input_codigo_mat_en_modal.val(data.materias[0].codigo);
                    }else{
                        var html_dropdown = '';
                        for(var i in data.materias){
                            html_dropdown += '<option value="' + data.materias[i].nombre + '">' + data.materias[i].codigo+" - " +data.materias[i].nombre+ '</option>';

                        }
                        dowpdown_opciones_materias_nombres.html(html_dropdown);
                    }
                }else{
                    console.log("Ocurrió un error obteniendo materias");
                }
        }
    );
});
/***************************************************************************************************/

/************************ Codigo para el modal agregar trimestre ***********************+*/
var modal_agregar_trim = $("#modal-agregar-trim");
var select_periodo = modal_agregar_trim.find("#id_select_periodo");
var select_anyo    = modal_agregar_trim.find("#id_select_anyo");

modal_agregar_trim.on('show.bs.modal', function (event) {
    // Si el usuario no tiene trimestres en el plan
    // Se le coloca por default Septiembre - Diciembre del año actual
    if(plan_creado_json.trimestres_planeados.length == 0){
        select_periodo.val('SD');
        select_anyo.val(new Date().getFullYear());
    }else{
        // Sino se le coloca por default el siguiente periodo al último creado
        var last_trim = plan_creado_json.trimestres_planeados[plan_creado_json.trimestres_planeados.length - 1];
        switch (last_trim.periodo){
            case 'SD':
                select_periodo.val('EM');
                select_anyo.val(parseInt(last_trim.anyo) + 1);
                break;
            case 'EM':
                select_periodo.val('AJ');
                select_anyo.val(last_trim.anyo);
                break;
            case 'AJ':
                select_periodo.val('JA');
                select_anyo.val(last_trim.anyo);
                break;
            case 'JA':
                select_periodo.val('SD');
                select_anyo.val(parseInt(last_trim.anyo) + 1);
                break;

        }
    }

});

modal_agregar_trim.find('#btn-agregar-trim').click(function (event) {

    var nuevo_trim_js = {};
    nuevo_trim_js.materias = [];
    nuevo_trim_js.periodo = select_periodo.val();
    nuevo_trim_js.anyo = select_anyo.val();
    nuevo_trim_js.codigo = next_cod_trime++;

    var n_trimestres = plan_creado_json.trimestres_planeados.length;
    plan_creado_json.trimestres_planeados[n_trimestres] = nuevo_trim_js;

    var nueva_tabla_trim_jq = $(crear_html_tabla_trimestre(n_trimestres)).hide();
    nueva_tabla_trim_jq.insertBefore(boton_agregar_trim);

    nueva_tabla_trim_jq.show('slow');

    actualizar_datos_plan_creado();

    modal_agregar_trim.modal("hide");
    btn_guardar_cambios.text("Guardar Cambios*");
    btn_guardar_cambios.removeAttr("disabled");
});
/***************************************************************************************************/


// Una vez que se ha cargado el documento
// Se debe hacer la petición al servidor de los datos del plan
// El cual regresará un json con dichos datos
// una vez obtenidos se debe crear la vista del usuario

/**
 * Carga los datos del plan con id = codigo
 * @param codigo
 */
function cargar_datos_plan(codigo){
    div_datos_trimestres_html.html('Cargando plan <img src=' + path_image_gear + '  style="width: 40px;height:40px;">');

    var msg_cargando_plan = alertify.notify('Cargando plan <img src=' + path_image_gear + '  style="width: 40px;height:40px;">','custom',0,null);


    $.get(location.origin + "/api/planes_creados/" + codigo + "/",
        function(data, status){
            if (status == "success"){
                alertify.success('¡Plan Cargado!');
                plan_creado_json = data;

                crear_tabla_trimestres();
                actualizar_datos_plan_creado();
                msg_cargando_plan.dismiss();

            }else{
                alertify.error("Ocurrió un error cargando los datos del plan :(");
            }
        }
    );
}
