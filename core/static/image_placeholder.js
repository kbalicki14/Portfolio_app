function readURL(id_image) {
    if (id_image.files && id_image.files[0]) {
        var reader = new FileReader();

        reader.onload = function(e) {
            $('#current').attr('src', e.target.result);
        }

        reader.readAsDataURL(id_image.files[0]); // convert to base64 string
    }
}

$("#id_image").change(function() {
    readURL(this);
});