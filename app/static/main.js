$(document).ready(function () {
  create_tasks_table()
})

$(document).on('shown.bs.tab', 'a[data-toggle="tab"]', function (e) {
  console.table(e)
  if (e.target.id === 'notes_tab') {
    create_notes_table()
  }
})

function create_notes_table () {
  console.log(get_route_for_entity('Note'))
  let notes_table = $('#notes_table').DataTable({
    retrieve: true,
    select: true,
    scrollY: 800,
    ajax: get_route_for_entity('Note'),
    columns: [{ data: 'image' }, { data: 'subject' }, { data: 'note_links' }],
    columnDefs: [
      {
        targets: [0],
        searchable: false,
        sortable: false,
        render: function (data) {
          return '<img src="' + data + '">'
        }
      },
      {
        targets: [1],
        render: function (data, type, row) {
          return '<a href="' + row.url + '">' + data + '</a>'
        }
      },
      {
        targets: [2],
        render: function (links, type, row) {
          let html = ''
          links.forEach(
            link =>
              (html += '<a href="' + link.url + '">' + link.name + '</a><br>')
          )
          return html
        }
      }
    ]
  })
  return notes_table
}

function create_tasks_table () {
  let tasks_table = $('#tasks_table').DataTable({
    select: true,
    scrollY: 800,
    ajax: get_route_for_entity('Task'),
    columns: [
      { data: 'image' },
      { data: 'content' },
      { data: 'entity' },
      { data: 'entity.type' }
    ],
    columnDefs: [
      {
        targets: [0],
        searchable: false,
        sortable: false,
        render: function (data) {
          return '<img src="' + data + '">'
        }
      },
      {
        targets: [1],
        render: function (data, type, row) {
          return '<a href="' + row.url + '">' + data + '</a>'
        }
      },
      {
        targets: [2],
        render: function (data) {
          return '<a href="' + data.url + '">' + data.name + '</a>'
        }
      }
    ]
  })
}

function get_route_for_entity (entity) {
  let user_id = $('#user_id').html()
  let url = 'http://127.0.0.1:5000/following/' + entity + '/' + user_id
  return url
}
