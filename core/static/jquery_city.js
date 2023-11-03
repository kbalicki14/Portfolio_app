$( function() {
    $( ".town-search" ).autocomplete({
      source: 'http://127.0.0.1:8000/advertise_create/',
      minLength: 2

    });

  } );
