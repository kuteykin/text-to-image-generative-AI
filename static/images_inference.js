$(document).ready(function() {
    $('#inference-form').submit(function(e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/inference',
            data: $('#inference-form').serialize(),
            success: function(response) {
                // Display the generated images
                var images = response.images;
                var outputDiv = $('#output');
                outputDiv.empty();
                for (var i = 0; i < images.length; i++) {
                    outputDiv.append('<img src="data:image/png;base64,' + images[i] + '">');
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});