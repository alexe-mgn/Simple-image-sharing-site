function upload_rating(val) {
    let dom = $('#rate_form')[0];

    let b_obj = $("label[for='rate0']");
    b_obj.hide();

    let badge = get_badge(dom);
    badge_set_loading(badge);

    if (0 <= val && val <= 6) {
        $.ajax('/post_rating/'.concat(post_id.toString(), '/', val.toString()), {method: 'POST', data: ''})
            .done(function (data) {
                if (data.success === true) {
                    $("input[name='rate']:checked").prop('checked', false);
                    $(`input[name='rate'][value=${val}]`).prop('checked', true);
                    badge_unset(badge);
                    b_obj.show()
                } else {
                    badge_set_error(badge, data.error || 'Ответ не был получен')
                }
            })
            .fail(function (xhr) {
                badge_set_error(badge, xhr.status.toString().concat(' - ', xhr.statusText));
            });
    } else {
        badge_set_error(badge, 'Неверное значение')
    }
}

$(function () {
    $('input[name="rate"]').on('click', function (event) {
        event.preventDefault();
        upload_rating(parseInt($(this).val()))
    });
});