import {
    login,
    register,
} from "./api.js";

const loginForm =
    document.getElementById(
        "login-form"
    ) as HTMLFormElement | null;


const registerForm =
    document.getElementById(
        "register-form"
    ) as HTMLFormElement | null;

const passwordRequirements =
    document.getElementById(
        "password-requirements"
    ) as HTMLElement | null;

const passwordConfirmationError =
    document.getElementById(
        "password-confirmation-error"
    ) as HTMLElement | null;

const emailError =
    document.getElementById(
        "email-error"
    ) as HTMLElement | null;


function showError(
    form: HTMLFormElement,
    message: string
): void {

    const existingError =
        form.querySelector(
            ".auth-error"
        );

    if (existingError) {
        existingError.remove();
    }

    const errorElement =
        document.createElement("div");

    errorElement.className =
        "auth-error";

    errorElement.textContent =
        message;

    form.prepend(
        errorElement
    );
}


function clearError(
    form: HTMLFormElement
): void {

    const existingError =
        form.querySelector(
            ".auth-error"
        );

    if (existingError) {
        existingError.remove();
    }
}

function isValidPassword(
    password: string
): boolean {

    return (
        password.length >= 8 &&
        /[A-Za-z]/.test(password) &&
        /\d/.test(password) &&
        /[^A-Za-z\d]/.test(password)
    );
}

function showPasswordConfirmationError(
    message: string
): void {

    if (!passwordConfirmationError) {
        return;
    }

    passwordConfirmationError.textContent =
        message;

    passwordConfirmationError.hidden =
        false;
}


function clearPasswordConfirmationError(): void {

    if (!passwordConfirmationError) {
        return;
    }

    passwordConfirmationError.textContent =
        "";

    passwordConfirmationError.hidden =
        true;
}

function showEmailError(
    message: string
): void {

    if (!emailError) {
        return;
    }

    emailError.textContent =
        message;

    emailError.hidden =
        false;
}


function clearEmailError(): void {

    if (!emailError) {
        return;
    }

    emailError.textContent =
        "";

    emailError.hidden =
        true;
}


async function handleLogin(
    event: SubmitEvent
): Promise<void> {

    event.preventDefault();

    if (!loginForm) {
        return;
    }

    clearError(loginForm);

    const emailInput =
        document.getElementById(
            "email"
        ) as HTMLInputElement;

    const passwordInput =
        document.getElementById(
            "password"
        ) as HTMLInputElement;

    const submitButton =
        loginForm.querySelector(
            'button[type="submit"]'
        ) as HTMLButtonElement;

    const email =
        emailInput.value.trim();

    const password =
        passwordInput.value;

    submitButton.disabled = true;
    submitButton.textContent =
        "Iniciando sesión...";

    try {

        const response =
            await login({
                email,
                password,
            });

        localStorage.setItem(
            "access_token",
            response.access_token
        );

        window.location.href =
            "./chat.html";

    } catch (error) {

        showError(
            loginForm,
            error instanceof Error
                ? error.message
                : "No se ha podido iniciar sesión."
        );

    } finally {

        submitButton.disabled = false;
        submitButton.textContent =
            "Iniciar sesión";
    }
}


async function handleRegister(
    event: SubmitEvent
): Promise<void> {

    event.preventDefault();

    if (!registerForm) {
        return;
    }

    clearError(registerForm);

    clearEmailError();

    const nameInput =
        document.getElementById(
            "name"
        ) as HTMLInputElement;

    const emailInput =
        document.getElementById(
            "email"
        ) as HTMLInputElement;

    const passwordInput =
        document.getElementById(
            "password"
        ) as HTMLInputElement;

    const confirmationInput =
        document.getElementById(
            "password-confirmation"
        ) as HTMLInputElement;

    const submitButton =
        registerForm.querySelector(
            'button[type="submit"]'
        ) as HTMLButtonElement;

    const name =
        nameInput.value.trim();

    const email =
        emailInput.value.trim();

    const password =
        passwordInput.value;

    const passwordConfirmation =
        confirmationInput.value;


    if (!isValidPassword(password)) {

        if (passwordRequirements) {
            passwordRequirements.classList.add(
                "invalid"
            );
        }

        return;
    }

    if (
        password !==
        passwordConfirmation
    ) {

        showPasswordConfirmationError(
            "Las contraseñas no coinciden."
        );

        return;
    }

    clearPasswordConfirmationError();

    if (passwordRequirements) {
        passwordRequirements.classList.remove(
            "invalid"
        );
    }


    submitButton.disabled = true;
    submitButton.textContent =
        "Creando cuenta...";


    try {

        await register({
            name,
            email,
            password,
        });

        window.location.href =
            "./login.html";

    } catch (error) {

        if (
            error instanceof Error &&
            error.message ===
                "El email ya está registrado."
        ) {

            showEmailError(
                "El email ya está registrado."
            );

        } else {

            showError(
                registerForm,
                error instanceof Error
                    ? error.message
                    : "No se ha podido crear la cuenta."
            );
        }

    } finally {

        submitButton.disabled = false;
        submitButton.textContent =
            "Crear cuenta";
    }
}


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        handleLogin
    );
}


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        handleRegister
    );
}

if (registerForm) {

    const passwordInput =
        document.getElementById(
            "password"
        ) as HTMLInputElement;

    const confirmationInput =
        document.getElementById(
            "password-confirmation"
        ) as HTMLInputElement;

    passwordInput.addEventListener(
        "input",
        () => {

            if (isValidPassword(passwordInput.value)) {

                passwordInput.classList.remove(
                    "input-error"
                );
            }
        }
    );

    confirmationInput.addEventListener(
        "input",
        () => {

            clearPasswordConfirmationError();
        }
    );
}

if (registerForm) {

    const emailInput =
        document.getElementById(
            "email"
        ) as HTMLInputElement;

    emailInput.addEventListener(
        "input",
        () => {
            clearEmailError();
        }
    );
}