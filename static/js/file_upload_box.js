$(function () {
    init_file_box($('#file_box')[0])
});

function init_file_box(form) {

    form.innerHTML = `
    <div class="box__input">
        <div class="box__icon fas fa-cloud-upload-alt fa-4x text-center mb-3">
        </div>
        <input type="file" name="files[]" id="file" class="box__file"
               data-multiple-caption="{count} files selected" multiple="">
        <label for="file" class="text-center m-auto">
            <strong>Choose a file</strong>
            <span class="box__dragndrop"> or drag it here</span></label>
        <button type="submit" class="box__button">Upload</button>
    </div>

    <div class="box__uploading">Uploading…</div>
    <div class="box__success">
        <img alt="Image" src="/image/alt">
    </div>
    <div class="box__error">Error!<span></span><a class="box__restart" role="button">Try again!</a></div>
    `;

    var input = form.querySelector('input[type="file"]');
    var label = form.querySelector('label');
    var errorMsg = form.querySelector('.box__error span');
    var restart = form.querySelectorAll('.box__restart');
    var droppedFiles = false;

    var saveImage = function () {
        console.log(droppedFiles);
        if (form.classList.contains('is-uploading')) return false;

        form.classList.add('is-uploading');
        form.classList.remove('is-error');

        let fr = new FileReader();
        fr.onload = function () {
            
        };

        form.classList.remove('is-uploading');
        form.classList.add('is-success')
    };

    input.addEventListener('change', function (e) {
        saveImage();
    });

    ['drag', 'dragstart', 'dragend', 'dragover', 'dragenter', 'dragleave', 'drop'].forEach(function (event) {
        form.addEventListener(event, function (e) {
            // preventing the unwanted behaviours
            e.preventDefault();
            e.stopPropagation();
        });
    });
    ['dragover', 'dragenter'].forEach(function (event) {
        form.addEventListener(event, function () {
            form.classList.add('is-dragover');
        });
    });
    ['dragleave', 'dragend', 'drop'].forEach(function (event) {
        form.addEventListener(event, function () {
            form.classList.remove('is-dragover');
        });
    });
    form.addEventListener('drop', function (e) {
        droppedFiles = e.dataTransfer.files;
        saveImage();
    });


    // restart the form if has a state of error/success
    Array.prototype.forEach.call(restart, function (entry) {
        entry.addEventListener('click', function (e) {
            e.preventDefault();
            form.classList.remove('is-error', 'is-success');
            input.click();
        });
    });

    // Firefox focus bug fix for file input
    input.addEventListener('focus', function () {
        input.classList.add('has-focus');
    });
    input.addEventListener('blur', function () {
        input.classList.remove('has-focus');
    });

}

