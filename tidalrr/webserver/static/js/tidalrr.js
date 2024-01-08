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
function queueArtist(artistId) {
  fetch('/tidal/artist/' + artistId+'/queue', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Artist queued successfully!');
      window.location.reload();
    } else {
      console.log('Error queueing artist');
    }
  })
}
function unqueueArtist(artistId) {
    fetch('/tidal/artist/' + artistId+'/unqueue', {
      method: 'POST'
    })
    .then(response => {
      if(response.ok) {
        console.log('Artist queued successfully!');
        window.location.reload();
      } else {
        console.log('Error queueing artist');
      }
    })
  }

// Download queued artists
function downloadArtist(artistId) {
  fetch('/tidal/artist/' + artistId+'/download', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Artists downloaded successfully!');
      window.location.reload();
    } else {
      console.log('Error downloading artists');
    }
  })
}
// Queue album
function queueAlbum(albumId) {
  fetch('/tidal/album/' + albumId + '/queue', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Album queued successfully!');
      window.location.reload();
    } else {
      console.log('Error queueing album');
    }
  })
}

function unqueueAlbum(albumId) {
  fetch('/tidal/album/' + albumId + '/unqueue', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Album unqueued successfully!');
      window.location.reload();
    } else {
      console.log('Error unqueueing album');
    }
  })
}

// Download queued albums
function downloadAlbum(albumId) {
  fetch('/tidal/album/'+albumId+'/download', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Albums downloaded successfully!');
      window.location.reload();
    } else {
      console.log('Error downloading albums');
    }
  })
}
// Queue playlist
function queuePlaylist(playlistId) {
  fetch('/tidal/playlist/' + playlistId + '/queue', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Playlist queued successfully!');
      window.location.reload();
    } else {
      console.log('Error queueing playlist');
    }
  })
}

function unqueuePlaylist(playlistId) {
  fetch('/tidal/playlist/' + playlistId + '/unqueue', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Playlist unqueued successfully!');
      window.location.reload();
    } else {
      console.log('Error unqueueing playlist');
    }
  })
}

// Download queued playlists
function downloadPlaylist(playlistId) {
  fetch('/tidal/playlist/' + playlistId + '/download', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('Playlists downloaded successfully!');
      window.location.reload();
    } else {
      console.log('Error downloading playlists');
    }
  }) 
}
// Queue track
function queueTrack(trackId) {
  fetch('/tidal/track/' + trackId + '/queue', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('track queued successfully!');
      window.location.reload();
    } else {
      console.log('Error queueing track');
    }
  })
}

function unqueueTrack(trackId) {
  fetch('/tidal/track/' + trackId + '/unqueue', {
    method: 'POST'
  })
  .then(response => {
    if(response.ok) {
      console.log('track unqueued successfully!');
      window.location.reload();
    } else {
      console.log('Error unqueueing track');
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
