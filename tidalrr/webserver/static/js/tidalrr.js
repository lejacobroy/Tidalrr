$(document).ready( function () {
  $('#table').DataTable({
    initComplete: function () {
      this.api().columns().every( function () {
        var column = this;
        var select = $('<select><option value=""></option></select>')
          .appendTo( $(column.footer()).empty() )
          .on( 'change', function () {
            var val = $.fn.dataTable.util.escapeRegex(
              $(this).val()
            );
            column
              .search( val ? '^'+val+'$' : '', true, false )
              .draw();
          } );

        column.data().unique().sort().each( function ( d, j ) {
          select.append( '<option value="'+d+'">'+d+'</option>' )
        } );
      });
    }
  });
  
  // Search input
  $('#search').on('keyup change', function(){
    table.search($(this).val()).draw();
  })
});

    // Queue artist
function monitorArtist(artistId) {
  fetch('/tidal/artist/' + artistId+'/monitor', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Artist monitored successfully!');
      window.location.reload();
    } else {
      console.log('Error queueing artist');
    }
  })
}
function unmonitorArtist(artistId) {
    fetch('/tidal/artist/' + artistId+'/unmonitor', {
      method: 'POST'
    })
    .then(response => {
      if(response.ok) {
        console.log('Artist unmonitored successfully!');
        window.location.reload();
      } else {
        console.log('Error queueing artist');
      }
    })
  }

// Queue album
function monitorAlbum(albumId) {
  fetch('/tidal/album/' + albumId + '/monitor', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Album monitored successfully!');
      window.location.reload();
    } else {
      console.log('Error queueing album');
    }
  })
}

function unmonitorAlbum(albumId) {
  fetch('/tidal/album/' + albumId + '/unmonitor', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Album unmonitored successfully!');
      window.location.reload();
    } else {
      console.log('Error unqueueing album');
    }
  })
}


// Queue playlist
function monitorPlaylist(playlistId) {
  fetch('/tidal/playlist/' + playlistId + '/monitor', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Playlist monitored successfully!');
      window.location.reload();
    } else {
      console.log('Error queueing playlist');
    }
  })
}

function unmonitorPlaylist(playlistId) {
  fetch('/tidal/playlist/' + playlistId + '/unmonitor', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Playlist unmonitored successfully!');
      window.location.reload();
    } else {
      console.log('Error unqueueing playlist');
    }
  })
}

// Download queued tracks
function downloadTrack(trackId) {
  fetch('/tidal/track/'+ trackId + '/download', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('tracks downloaded successfully!');
      window.location.reload();
    } else {
      console.log('Error downloading tracks');
    }
  })
}
