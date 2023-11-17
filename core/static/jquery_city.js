$( function() {
    $( ".town-search" ).autocomplete({
//    hardcoded url not for deploy!
      source: 'http://127.0.0.1:8000/search_tooltip/',
      minLength: 2

    });

  } );
