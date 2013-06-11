function hide_msg() {
    $("#message").slideUp();
}

$(document).ready(function() {
    window.setTimeout(hide_msg, 3000);
});
