$( function() {
    $( ".town-search" ).autocomplete({
//    hardcoded url not for deploy!
      source: 'https://comfortable-rosamund-projects-django-080370fd.koyeb.app/search_tooltip/',
//      source: 'http://127.0.0.1:8000/search_tooltip/',
      minLength: 2

    });

  } );
