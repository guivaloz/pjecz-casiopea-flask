/* DataTables función toggleEsActivo para los botones que cambian es_activo
 *
 * Ejemplo de uso en la configuración de DataTables para Oficinas:
 *
 * configDTOficinas['columnDefs'] = [
 *   {
 *     targets: 7, // toggle_es_activo
 *     data: null,
 *     render: function(data, type, row, meta) {
 *       if (data.url === '') {
 *         if (data.es_activo === true) {
 *           return '<span class="badge bg-primary">Activo</span>';
 *         } else {
 *           return '<span class="badge bg-secondary">Inactivo</span>';
 *         }
 *       }
 *       let myId = 'oficinas_es_activo_' + data.id;
 *       let myRow = 'oficinas_row_' + data.id;
 *       let myOnClick = "toggleEsActivo('#" + myId + "', '" + data.url + "', '#" + myRow + "')";
 *       if (data.es_activo === true) {
 *         return '<button id="' + myId + '" type="button" class="btn btn-sm btn-outline-primary" onclick="' + myOnClick + '"><span class="mdi mdi-toggle-switch"></span></button>';
 *       } else {
 *         return '<button id="' + myId + '" type="button" class="btn btn-sm btn-light" onclick="' + myOnClick + '"><span class="mdi mdi-toggle-switch-off"></span></button>';
 *       }
 *     }
 *   }
 * ];
 */

// Boton toggle_es_activo
function toggleEsActivo(id, url, row) {
  // Mostrar mensaje de error en la consola si no se tiene myInit
  if (!myInit) {
    console.log("Error: myInit no está definido");
    return;
  }
  // Cambiar el estado de es_activo mediante fetch API y cambiar el botón y la fila de la tabla
  $(id).prop("disabled", true); // Deshabilitar boton para evitar multiples clicks
  fetch(url, myInit)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        if (data.es_activo === true) {
          $(id).removeClass("btn-light");
          $(id).addClass("btn-outline-primary"); // Color azul
          $(id).html(
            '<span class="mdi mdi-toggle-switch"></span>'
          ); // Icono toggle-switch
          $(row).removeClass("table-secondary");
        } else {
          $(id).removeClass("btn-outline-primary");
          $(id).addClass("btn-light"); // Color gris
          $(id).html(
            '<span class="mdi mdi-toggle-switch-off"></span>'
          ); // Icono toggle-switch-off
          $(row).addClass("table-secondary");
        }
      }
      $(id).prop("disabled", false); // Habilitar boton
    })
    .catch((error) => {
      console.log(error);
    });
}
