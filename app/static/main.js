$(document).ready(function () {
  create_tasks_table()
})

$(document).on('shown.bs.tab', 'a[data-toggle="tab"]', function (e) {
  if (e.target.id === 'notes_tab') {
    create_notes_table()
  } else if (e.target.id === 'assets_tab') {
    create_assets_table()
  }
})

function create_notes_table () {
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

function create_assets_table () {
  let assets_table = $('#assets_table').DataTable({
    retrieve: true,
    select: true,
    scrollY: 800,
    ajax: get_route_for_entity('Asset'),
    columns: [{ data: 'image' }, { data: 'code' }],
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
      }
    ]
  })
  return assets_table
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
  let url = '/following/' + entity + '/' + user_id
  return url
}

function unfollow () {
  let user_id = parseInt($('#user_id').html())
  let selected_entities = []
  // get all the tables with sg-table class and then get all their selected rows
  let selected_rows = $('.sg-table')
    .DataTable()
    .rows({ selected: true })
  selected_rows
    .data()
    .each(row => selected_entities.push({ id: row.id, type: row.type }))

  // post the entities to the flask server to do the unfollowing
  fetch('/unfollow', {
    method: 'POST',
    body: JSON.stringify({
      entities: selected_entities,
      user_id: user_id
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(resp => resp.json()) // Transform the data into json
    .then(function (data) {
      selected_rows.remove().draw()
    })
    .catch(error => console.error('err' + error))
}
