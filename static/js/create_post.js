$(function () {
    let image_input = document.getElementById('image_input');
    let badge = $('form .status-badge')[0];

    $(image_input).on('change', function () {
        let fr = new FileReader();
        fr.onload = function () {
            document.getElementById('image').src = fr.result
        };
        fr.readAsDataURL(this.files[0]);
        badge_unset(badge)
    });

    $("form").on('submit', function (e) {
        let form_dom = this;
        e.preventDefault();
        e.stopPropagation();
        badge_set_loading(badge);
        if (!image_input.files.length) {
            badge_set_error(badge, 'Необходимо загрузить изображение')
        } else {
            $.ajax(form_dom.action, {
                method: 'POST',
                data: new FormData(form_dom),
                processData: false,
                contentType: false
            })
                .done(function (data) {
                    if (data.success === true) {
                        badge_unset(badge);
                        window.history.back()
                    } else {
                        badge_set_error(badge, data.error || 'Ответ не был получен')
                    }
                })
                .fail(function (xhr) {
                    badge_set_error(badge, xhr.status.toString().concat(' - ', xhr.statusText))
                })
        }
        return false
    })
});