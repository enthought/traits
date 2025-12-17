// In long descclassnames, allow word-wrapping on periods.

$(document).ready(function() {
    $('.descclassname').html(function(index, html) {
        return html.replace(/\./g, '.<wbr>');
    });
});
