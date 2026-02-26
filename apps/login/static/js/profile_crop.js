document.addEventListener('DOMContentLoaded', function () {
    const avatarInput = document.getElementById('id_avatar');
    const modal = document.getElementById('avatar-cropper-modal');
    const cropImage = document.getElementById('avatar-cropper-image');
    const cancelBtn = document.getElementById('cancel-avatar-crop');
    const applyBtn = document.getElementById('apply-avatar-crop');
    const previewImg = document.getElementById('current-avatar-preview');

    if (!avatarInput || !modal || !cropImage || !cancelBtn || !applyBtn || !previewImg) {
        return;
    }

    let cropper = null;
    let sourceObjectUrl = null;
    let previewObjectUrl = null;

    const closeCropperModal = () => {
        modal.classList.remove('is-open');
        modal.setAttribute('aria-hidden', 'true');
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    };

    const openCropperWithFile = (file) => {
        if (!file) {
            alert('Selecciona una imagen primero.');
            return;
        }
        if (typeof Cropper === 'undefined') {
            alert('No se pudo cargar el recortador de imagen.');
            return;
        }

        if (sourceObjectUrl) {
            URL.revokeObjectURL(sourceObjectUrl);
        }
        sourceObjectUrl = URL.createObjectURL(file);
        cropImage.src = sourceObjectUrl;
        modal.classList.add('is-open');
        modal.setAttribute('aria-hidden', 'false');
    };

    cropImage.addEventListener('load', function () {
        if (cropper) {
            cropper.destroy();
        }
        cropper = new Cropper(cropImage, {
            aspectRatio: 1,
            viewMode: 1,
            dragMode: 'move',
            autoCropArea: 1,
            background: false,
            responsive: true
        });
    });

    previewImg.addEventListener('click', function () {
        const file = avatarInput.files && avatarInput.files[0] ? avatarInput.files[0] : null;
        if (file) {
            openCropperWithFile(file);
        } else {
            avatarInput.click();
        }
    });

    avatarInput.addEventListener('change', function () {
        const file = avatarInput.files && avatarInput.files[0] ? avatarInput.files[0] : null;
        if (file) {
            openCropperWithFile(file);
        }
    });

    cancelBtn.addEventListener('click', closeCropperModal);

    applyBtn.addEventListener('click', function () {
        if (!cropper) {
            return;
        }

        const canvas = cropper.getCroppedCanvas({
            width: 512,
            height: 512,
            imageSmoothingQuality: 'high'
        });

        if (!canvas) {
            return;
        }

        canvas.toBlob(function (blob) {
            if (!blob) {
                return;
            }

            const croppedFile = new File([blob], 'avatar-cropped.png', { type: 'image/png' });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(croppedFile);
            avatarInput.files = dataTransfer.files;

            if (previewImg) {
                if (previewObjectUrl) {
                    URL.revokeObjectURL(previewObjectUrl);
                }
                previewObjectUrl = URL.createObjectURL(blob);
                previewImg.src = previewObjectUrl;
            }

            closeCropperModal();
        }, 'image/png');
    });
});
