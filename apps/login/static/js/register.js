document.addEventListener('DOMContentLoaded', function () {
    const usernameInput = document.getElementById('id_username');
    const emailInput = document.getElementById('id_email');
    const pass1Input = document.getElementById('id_password1');
    const pass2Input = document.getElementById('id_password2');
    const submitBtn = document.getElementById('submit-btn');

    const urls = {
        checkAvailability: '/login/check_availability/',
        validatePassword: '/login/validate_password/'
    };

    let isUsernameValid = false;
    let isEmailValid = false;
    let isPasswordValid = false;
    let passwordsMatch = false;
    let passwordValidationRequestId = 0;

    function updateSubmitButton() {
        submitBtn.disabled = !(isUsernameValid && isEmailValid && isPasswordValid && passwordsMatch);
        submitBtn.style.opacity = submitBtn.disabled ? '0.5' : '1';
    }

    function triggerPasswordRevalidation() {
        if (pass1Input && pass1Input.value) {
            pass1Input.dispatchEvent(new Event('input'));
        }
    }

    // Validación de Apodo
    if (usernameInput) {
        usernameInput.addEventListener('input', async function () {
            const value = this.value;
            const msgDiv = document.getElementById('msg-id_username');
            const wrapper = document.getElementById('wrapper-id_username');

            if (value.length < 3) {
                msgDiv.classList.remove('visible');
                wrapper.classList.remove('valid-field', 'invalid-field');
                isUsernameValid = false;
            } else {
                try {
                    const response = await fetch(`${urls.checkAvailability}?username=${encodeURIComponent(value)}`);
                    const data = await response.json();
                    if (data.is_taken) {
                        msgDiv.innerHTML = '✗ Apodo ya en uso';
                        msgDiv.className = 'validation-msg visible msg-error';
                        wrapper.classList.add('invalid-field');
                        wrapper.classList.remove('valid-field');
                        isUsernameValid = false;
                    } else {
                        msgDiv.innerHTML = '✓ ¡Apodo disponible!';
                        msgDiv.className = 'validation-msg visible msg-success';
                        wrapper.classList.add('valid-field');
                        wrapper.classList.remove('invalid-field');
                        isUsernameValid = true;
                    }
                } catch (err) { console.error(err); }
            }
            updateSubmitButton();
            triggerPasswordRevalidation();
        });
    }

    // Validación de Email
    if (emailInput) {
        emailInput.addEventListener('input', async function () {
            const value = this.value;
            const msgDiv = document.getElementById('msg-id_email');
            const wrapper = document.getElementById('wrapper-id_email');
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!emailRegex.test(value)) {
                msgDiv.innerHTML = '✗ Formato de email inválido';
                msgDiv.className = 'validation-msg visible msg-error';
                wrapper.classList.add('invalid-field');
                wrapper.classList.remove('valid-field');
                isEmailValid = false;
            } else {
                try {
                    const response = await fetch(`${urls.checkAvailability}?email=${encodeURIComponent(value)}`);
                    const data = await response.json();
                    if (data.is_taken) {
                        msgDiv.innerHTML = '✗ Email ya registrado';
                        msgDiv.className = 'validation-msg visible msg-error';
                        wrapper.classList.add('invalid-field');
                        wrapper.classList.remove('valid-field');
                        isEmailValid = false;
                    } else {
                        msgDiv.innerHTML = '✓ Email disponible';
                        msgDiv.className = 'validation-msg visible msg-success';
                        wrapper.classList.add('valid-field');
                        wrapper.classList.remove('invalid-field');
                        isEmailValid = true;
                    }
                } catch (err) { console.error(err); }
            }
            updateSubmitButton();
            triggerPasswordRevalidation();
        });
    }

    // Validación de Password 1
    if (pass1Input) {
        pass1Input.addEventListener('input', async function () {
            const value = this.value;
            const msgDiv = document.getElementById('msg-id_password1');
            const wrapper = document.getElementById('wrapper-id_password1');
            const requestId = ++passwordValidationRequestId;

            if (value.length === 0) {
                msgDiv.classList.remove('visible');
                wrapper.classList.remove('valid-field', 'invalid-field');
                isPasswordValid = false;
                checkMatch();
                updateSubmitButton();
                return;
            }

            try {
                const params = new URLSearchParams({
                    password: value,
                    username: usernameInput ? usernameInput.value : '',
                    email: emailInput ? emailInput.value : '',
                });
                const response = await fetch(`${urls.validatePassword}?${params.toString()}`);
                const data = await response.json();

                if (requestId !== passwordValidationRequestId) {
                    return;
                }

                if (data.is_valid) {
                    msgDiv.innerHTML = '✓ Contraseña segura';
                    msgDiv.className = 'validation-msg visible msg-success';
                    wrapper.classList.add('valid-field');
                    wrapper.classList.remove('invalid-field');
                    isPasswordValid = true;
                } else {
                    const errors = Array.isArray(data.errors) ? data.errors : ['Contraseña inválida'];
                    const firstError = errors.length > 0 ? errors[0] : 'Contraseña inválida';
                    let friendlyError = firstError;
                    if (friendlyError && friendlyError.toLowerCase().includes('demasiado corta')) {
                        friendlyError = 'La contraseña debe contener por lo menos 8 caracteres';
                    }
                    msgDiv.innerHTML = `✗ ${friendlyError}`;
                    msgDiv.className = 'validation-msg visible msg-error';
                    wrapper.classList.add('invalid-field');
                    wrapper.classList.remove('valid-field');
                    isPasswordValid = false;
                }
            } catch (err) {
                console.error(err);
            }

            checkMatch();
            updateSubmitButton();
        });
    }

    function checkMatch() {
        if (!pass2Input) return;
        const p1 = pass1Input.value;
        const p2 = pass2Input.value;
        const msgDiv = document.getElementById('msg-id_password2');
        const wrapper = document.getElementById('wrapper-id_password2');

        if (p2.length === 0) {
            msgDiv.classList.remove('visible');
            wrapper.classList.remove('valid-field', 'invalid-field');
            passwordsMatch = false;
        } else if (p1 === p2) {
            msgDiv.innerHTML = '✓ Las contraseñas coinciden';
            msgDiv.className = 'validation-msg visible msg-success';
            wrapper.classList.add('valid-field');
            wrapper.classList.remove('invalid-field');
            passwordsMatch = true;
        } else {
            msgDiv.innerHTML = '✗ Las contraseñas no coinciden';
            msgDiv.className = 'validation-msg visible msg-error';
            wrapper.classList.add('invalid-field');
            wrapper.classList.remove('valid-field');
            passwordsMatch = false;
        }
    }

    if (pass2Input) {
        pass2Input.addEventListener('input', () => {
            checkMatch();
            updateSubmitButton();
        });
    }
});
