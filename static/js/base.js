function set_input(dom, callback) {
    let obj = $(dom);
    dom = obj[0];

    let input = document.createElement("textarea");
    $.each(dom.attributes, function(n, atr) {
        input.setAttribute(atr.name, atr.value);
    });
    input.value = obj.text();
    input.style.width = '100%';
    input.style.fontSize = dom.style.fontSize;

    dom.parentNode.insertBefore(input, dom);
    obj.hide();

    input.focus();
    input.onblur = function () {
        dom.parentNode.removeChild(input);
        let value = input.value === "" ? "&nbsp;" : input.value;
        obj.show();
        if (callback)
            callback.bind(dom)(value)
    };
}


function text_update_input(eid) {
    let dom = $(eid)[0];
    set_input(dom, text_update_callback)
}


function text_update_callback(text) {
    let dom = this;
    let obj = $(dom);
    let api_link = obj.attr('text-update-url');
    let key = obj.attr('text-update-value');
    if (api_link && key) {
        if (text !== obj.text()) {
            let badge = get_badge(dom);
            badge_set_loading(badge);
            console.log(dom);
            console.log(badge);

            let data = {};
            data[key] = text;
            $.ajax(api_link, {
                method: 'PUT',
                data: JSON.stringify(data),
                contentType: 'application/json'
            })
                .done(function (data) {
                    if (data.success === true) {
                        obj.text(text);
                        badge_unset(badge)
                    } else {
                        badge_set_error(badge, (data.error || 'Ответ не был получен').concat('\nПовторить'));
                        $(badge).on('click', function () {
                            text_update_callback.bind(dom)(text)
                        });
                    }
                })
                .fail(function (xhr) {
                    badge_set_error(badge, xhr.status.toString().concat(' - ', xhr.statusText, '\nПовторить'));
                    $(badge).on('click', function () {
                        text_update_callback.bind(dom)(text)
                    });
                })
        }
    }
}

function badges_init() {
    $('.status-badge').each(function (n, dom) {
        let obj = $(dom);
        if (!obj.attr('loading-class')) {
            obj.attr('loading-class', 'spinner-border spinner-border-md text-primary');
        }
        obj.attr('data-html', true);
        obj.tooltip({placement: 'auto', title: ''});
        obj.html('!');
        obj.hide();
    });
}

function get_badge(dom) {
    return $($(dom).attr('status-badge'))[0]
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
        badge.attr('data-original-title', `<div class="tooltip-text">${msg}</div>`);
        badge.show()
    }
}

function badge_unset(dom) {
    $(dom).hide()
}

function resizeIFrameToFitContent(iFrame) {
    let obj = $(iFrame);
    // iFrame.style.width = iFrame.contentWindow.document.body.scrollWidth;
    // iFrame.style.height = iFrame.contentWindow.document.body.scrollHeight;
}

var reserved_frame;
var frame_url = '/api/image/alt';


function load_reserved(url) {
    frame_url = url;
    reserved_frame.src = url;
    $('#reserved_modal').modal('show')
}

$(document).ready(function () {
    reserved_frame = document.getElementById('reserved_frame');

    $("[data-toggle='tooltip']").tooltip();
    badges_init();

    resizeIFrameToFitContent(reserved_frame);

    $(reserved_frame).on('load', function () {
        let c_url = reserved_frame.contentWindow.location.pathname;
        if (c_url !== frame_url) {
            reserved_frame.src = frame_url;
            $('#reserved_modal').modal('hide')
        }
    })
});
