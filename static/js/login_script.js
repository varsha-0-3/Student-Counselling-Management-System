document.addEventListener("DOMContentLoaded", function () {
    $(".message a").click(function () {
        $("form").animate({
            height: "toggle",
            opacity: "toggle"
        }, "slow");
    });

    const registerForm = document.getElementById('register-form');
    const loginFormCounsellor = document.getElementById('login-form-counsellor');
    const loginFormStudent = document.getElementById('login-form-student');
    const modal = document.getElementById("errorModal");
    const modalMessage = document.getElementById("modal-error-message");
    const span = document.getElementsByClassName("close")[0];

    // Function to show the error modal
    function showErrorModal(message) {
        modalMessage.textContent = message;
        modal.style.display = "block";
    }

    // Validation functions
    function validateName(name) {
        const re = /^[a-zA-Z\s]*$/;
        return re.test(name);
    }

    function validateUsn(usn) {
        const re = /^1RV\d{2}[A-Z]{2,3}\d{3}$/;
        return re.test(usn);
    }

    function validatePhone(phone) {
        const re = /^\d{10}$/;
        return re.test(phone);
    }

    function validateEmail(email) {
        const re = /^[a-z0-9._%+-]+@rvce\.edu\.in$/;
        return re.test(email.toLowerCase());
    }

    function validatePassword(password) {
        return password.length >= 4;
    }

    function validateConfirmPassword(cpassword, form) {
        return cpassword === form['password'].value;
    }

    // Check and handle the registration form
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            let valid = true;

            const indicators = {
                name: { validate: validateName, message: "Please enter a valid name." },
                usn: { validate: validateUsn, message: "Please enter a valid USN." },
                phone: { validate: validatePhone, message: "Please enter a valid phone number." },
                email: { validate: validateEmail, message: "Please enter a valid email." },
                parent_phone: { validate: validatePhone, message: "Please enter a valid parent phone number." },
                parent_email: { validate: validateEmail, message: "Please enter a valid parent email." },
                password: { validate: validatePassword, message: "Password must be at least 4 characters." },
                cpassword: { validate: validateConfirmPassword, message: "Passwords do not match." }
            };

            for (const key in indicators) {
                const { validate, message } = indicators[key];
                const value = registerForm[key].value;
                if (!validate(value, registerForm)) {
                    showErrorModal(message);
                    valid = false;
                    break;
                }
            }

            if (valid) {
                registerForm.submit();
            }
        });
    }

    // Check and handle the student login form
    if (loginFormStudent) {
        loginFormStudent.addEventListener('submit', (e) => {
            e.preventDefault();
            let valid = true;
    
            const indicators = {
                usn: { validate: validateUsn, message: "Please enter a valid USN." },
                password: { validate: validatePassword, message: "Password must be at least 4 characters." }
            };
    
            const usnValue = loginFormStudent.usn.value;
            if (!indicators.usn.validate(usnValue, loginFormStudent)) {
                showErrorModal(indicators.usn.message);
                // Redirect to the login page with a hash fragment
                window.location.href = "{{ url_for('register_login_student') }}#";
                valid = false;
            }
    
            const passwordValue = loginFormStudent.password.value;
            if (!indicators.password.validate(passwordValue, loginFormStudent)) {
                showErrorModal(indicators.password.message);
                // Redirect to the login page with a hash fragment
                window.location.href = "{{ url_for('register_login_student') }}#";
                valid = false;
            }
    
            if (valid) {
                loginFormStudent.submit();
            }
        });
    }
    

    // Check and handle the counsellor login form
    if (loginFormCounsellor) {
        loginFormCounsellor.addEventListener('submit', (e) => {
            e.preventDefault();
            let valid = true;

            const indicators = {
                name: { validate: validateName, message: "Please enter a valid name." },
                password: { validate: validatePassword, message: "Password must be at least 4 characters." }
            };

            const nameValue = loginFormCounsellor.name.value;
            if (!indicators.name.validate(nameValue, loginFormCounsellor)) {
                showErrorModal(indicators.name.message);
                valid = false;
            }

            const passwordValue = loginFormCounsellor.password.value;
            if (!indicators.password.validate(passwordValue, loginFormCounsellor)) {
                showErrorModal(indicators.password.message);
                valid = false;
            }

            if (valid) {
                loginFormCounsellor.submit();
            }
        });
    }

    // Modal close functionality
    if (span) {
        span.onclick = function () {
            modal.style.display = "none";
        };
    }

    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
});
