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

function text_update_input(eid) {
    let dom = $(eid)[0];
    let api_link = $(dom).attr('text-update');
    if (api_link) {
        set_input(dom, function (text) {
            if (text !== $(dom).text()) {
                let badge = get_badge(dom);
                badge_set_loading(badge);
                $.ajax(api_link,
                    {method: 'POST', data: text})
                    .done(function (data) {
                        if (data.success === true) {
                            $(dom).text(text);
                            badge_unset(badge)
                        } else {
                            badge_set_error(badge, data.error || 'Ответ не был получен')
                        }
                    })
                    .fail(function (xhr) {
                        badge_set_error(badge, xhr.status.toString().concat(' ', xhr.statusText));
                    })
            }
        })
    }
}

// function text_editable_init() {
//     $('[text-editable]').each(function (n, dom) {
//         let obj = $(dom);
//         if ($(""))
//         if (!obj.attr('status-badge')) {
//             let nb =
//             obj.attr('status-badge', '#'.concat(bid));
//         }
//     })
// }

function badges_init() {
    $('.status-badge').each(function (n, dom) {
        let obj = $(dom);
        if (!obj.attr('loading-class')) {
            obj.attr('loading-class', 'spinner-border spinner-border-md text-primary');
        }
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
        badge.addClass(badge.attr('loading-class'));
        badge.html('');
        badge.show()
    }
}

function badge_set_error(dom, msg) {
    let badge = $(dom);
    if (badge) {
        badge.removeClass(badge.attr('loading-class'));
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
    badges_init()
});
