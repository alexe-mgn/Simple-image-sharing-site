$(function () {
    $('#avatar_input').on('change',
        avatar_upload.bind(document.getElementById('avatar_input'))
    );
});

function avatar_upload() {
    if (this.files.length > 0) {
        let dom = this;
        let form_data = new FormData();
        console.log(dom.files);
        form_data.append('avatar_image', dom.files[0]);
        let badge = get_badge(dom);
        badge_set_loading(badge);
        $.ajax("/api/upload_avatar",
            {method: "POST", processData: false, contentType: false, data: form_data})
            .done(function (data) {
                if (data.success === true) {
                    $('#avatar').attr('src', '/api/image/'.concat(data.id.toString()));
                    badge_unset(badge);
                    $('#avatarUploadModal').modal('hide')
                } else {
                    badge_set_error(badge, (data.error || 'Ответ не был получен').concat('\nПовторить'));
                    badge.onclick = avatar_upload.bind(dom)
                }
            })
            .fail(function (xhr) {
                badge_set_error(badge, xhr.status.toString().concat(' - ', xhr.statusText, '\nПовторить'));
                badge.onclick = avatar_upload.bind(dom)
            })
    }
}