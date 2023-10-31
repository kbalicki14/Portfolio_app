$( function() {
    $( "#id_town" ).autocomplete({
      source: 'http://127.0.0.1:8000/upload/',
      minLength: 2

    });

  } );
