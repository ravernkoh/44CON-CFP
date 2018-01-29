var editor;
$(document).ready(function(){
    $('#submissions').DataTable({
    dom: 'Blfrtip',
    colReorder: true,
    fixedHeader: true,
    pageLength: 10,
    select: true,
    responsive: true,
    buttons: [
      {
        text: 'This Years Submissions',
        action: function(e, dt, node, config) {
          dt.search('{% now "Y" %}').draw();
        },
        className: 'btn btn-primary'
      },
      {
        extend: 'collection',
        text: 'Export...',
        buttons: [
          'excel',
          'csv'
        ],
        className: 'btn btn-primary'
      }
    ]
  });
});
