function upload_rating(val) {
    let dom = $('#rate_form')[0];

    let b_obj = $("label[for='rate0']");
    b_obj.hide();

    let badge = get_badge(dom);
    badge_set_loading(badge);

    if (0 <= val && val <= 6) {
        $.ajax('/api/post/'.concat(post_id.toString()), {
            method: 'PUT',
            data: JSON.stringify({user_rating: val}),
            contentType: 'application/json'
        })
            .done(function (data) {
                if (data.success === true) {
                    // show_rating(data.value);
                    badge_unset(badge);
                    b_obj.show();
                    update_stats()
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


function show_user_rating(val) {
    $("input[name='rate']:checked").prop('checked', false);
    $(`input[name='rate'][value=${val}]`).prop('checked', true);
}


function update_stats() {
    $.ajax('/api/post/'.concat(post_id.toString()),
        {
            method: 'GET'
        })
        .done(function (data) {
            if (data.success) {
                $('#average_rating').text(data.data.rating);
                $('#comments_number').text(data.data.comments_number);
                show_user_rating(data.data.user_rating)
            }
        });
}


$(function () {
    $('input[name="rate"]').on('click', function (event) {
        event.preventDefault();
        let new_val = parseInt($(this).val());
        upload_rating(new_val)
    });
    update_stats();
});