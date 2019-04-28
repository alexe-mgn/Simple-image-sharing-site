$(function () {
    $('#avatar_input').on('change', function () {
        if (this.files.length > 0) {
            let dom = this;
            let form_data = new FormData();
            form_data.append('avatar_image', dom.files[0]);
            let badge = get_badge(dom);
            badge_set_loading(badge);
            $.ajax("/upload_avatar",
                {method: "POST", processData: false, contentType: false, data: form_data})
                .done(function (data) {
                    if (data.success === true) {
                        $('#avatar').attr('src', '/image/'.concat(data.id.toString()));
                        badge_unset(badge);
                        $('#avatarUploadModal').modal('hide')
                    } else {
                        badge_set_error(badge, data.error)
                    }
                })
                .fail(function (req, msg) {
                    badge_set_error(badge, msg)
                });
        }
    });
});

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
                        console.log(data.success === true);
                        if (data.success === true) {
                            $(dom).text(text);
                            badge_unset(badge)
                        } else {
                            badge_set_error(badge, data.error || 'Ответ не был получен')
                        }
                    })
                    .fail(function (req, msg) {
                        badge_set_error(msg)
                    })
                    .always(function (data) {
                        console.log(data)
                    })
            }
        })
    }
}