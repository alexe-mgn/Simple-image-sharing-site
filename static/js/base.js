function set_input(dom, callback) {
    // Get its text
    let obj = $(dom);

    // Create an input
    let input = document.createElement("textarea");
    input.value = obj.text();
    input.style.width = '100%';
    input.style.fontSize = dom.style.fontSize;

    dom.parentNode.insertBefore(input, dom);
    obj.hide();

    // Focus it, hook blur to undo
    input.focus();
    input.onblur = function () {
        // Remove the input
        dom.parentNode.removeChild(input);
        // Update the dom
        let value = input.value === "" ? "&nbsp;" : input.value;
        // Show the dom again
        obj.show();
        if (callback)
            callback(value)
    };
}

function reindex() {
    $('.status-badge').each(function (n, dom) {
        let obj = $(dom);
        obj.tooltip({placement: 'auto', title: ''});
        obj.html('!');
        obj.hide();
    });
}

function get_badge(dom) {
    return $(dom).attr('status-badge')
}

function badge_set_loading(dom) {
    let badge = $(dom);
    if (badge) {
        badge.removeClass('status-badge-error');
        badge.addClass('spinner-border');
        badge.addClass('spinner-border-md');
        badge.addClass('text-primary');
        badge.html('');
        badge.show()
    }
}

function badge_set_error(dom, msg) {
    let badge = $(dom);
    if (badge) {
        badge.removeClass('spinner-border');
        badge.removeClass('spinner-border-md');
        badge.removeClass('text-primary');
        badge.addClass('status-badge-error');
        badge.html('!');
        badge.attr('data-original-title', msg);
        badge.show()
    }
}

function badge_unset(dom) {
    $(dom).hide()
}

$(document).ready(function () {
    $("[data-toggle='tooltip']").tooltip();
    reindex()
});
