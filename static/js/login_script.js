document.addEventListener("DOMContentLoaded", function () {
    $(".message a").click(function () {
        $("form").animate({
            height: "toggle",
            opacity: "toggle"
        }, "slow");
    });

    const form = document.getElementById('register-form');
    const modal = document.getElementById("errorModal");
    const modalMessage = document.getElementById("modal-error-message");
    const span = document.getElementsByClassName("close")[0];

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

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        let valid = true;

        for (const key in indicators) {
            const { validate, message } = indicators[key];
            const value = form[key].value;
            if (!validate(value, form)) {
                showErrorModal(message);
                valid = false;
                break;
            }
        }

        if (valid) {
            form.submit();
        }
    });

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }

    function showErrorModal(message) {
        modalMessage.textContent = message;
        modal.style.display = "block";
    }

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
});
