$(document).ready(function() {
    $('.error-badge').each(function(n, dom) {
        let obj = $(dom);
        obj.tooltip({placement: 'auto', title: ''});
        obj.html('!');
        obj.hide()
    });
});