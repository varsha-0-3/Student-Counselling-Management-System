document.addEventListener("DOMContentLoaded", function () {
    $(".message a").click(function () {
        $("form").animate({
            height: "toggle",
            opacity: "toggle"
        }, "slow")
    });

    const Name = document.getElementById("name");
    const Usn = document.getElementById("usn");
    const Phone = document.getElementById("phone");
    const Email = document.getElementById("email");
    const Pass = document.getElementById("password");
    const CPass = document.getElementById("cpassword");

    const NameError = document.getElementById("error1");
    const UsnError= document.getElementById("error2");
    const PhoneError = document.getElementById("error3");
    const EmailError = document.getElementById("error4");
    const PassError = document.getElementById("error5");
    const CPassError = document.getElementById("error6");

    const Strength = document.getElementById("strength");
    const RegisterForm = document.getElementById("register-form");

    const indicator = document.querySelector(".indicator");
    const input = document.getElementById("password");
    const weak = document.querySelector(".weak");
    const medium = document.querySelector(".medium");
    const strong = document.querySelector(".strong");
    const text = document.querySelector(".strength");

    let regExpWeak = /[a-zA-Z]+/;
    let regExpMedium = /\d+/;
    let regExpStrong = /[!@#$%^&*?_~(),-]+/;

    function trigger() {
        let no;
        if (input.value !== "") {
            indicator.style.display = "block";
            indicator.style.display = "flex";
            if (input.value.length <= 3 && (input.value.match(regExpWeak) || input.value.match(regExpMedium) || input.value.match(regExpStrong))) no = 1;
            if (input.value.length >= 6 && ((input.value.match(regExpWeak) && input.value.match(regExpMedium)) || (input.value.match(regExpMedium) && input.value.match(regExpStrong)) || (input.value.match(regExpWeak) && input.value.match(regExpStrong)))) no = 2;
            if (input.value.length >= 6 && input.value.match(regExpWeak) && input.value.match(regExpMedium) && input.value.match(regExpStrong)) no = 3;
            if (no === 1) {
                weak.classList.add("active");
                text.style.display = "block";
                text.textContent = "Your password is too weak";
                text.classList.add("weak");
            }
            if (no === 2) {
                medium.classList.add("active");
                text.textContent = "Your password is medium";
                text.classList.add("medium");
            } else {
                medium.classList.remove("active");
                text.classList.remove("medium");
            }
            if (no === 3) {
                weak.classList.add("active");
                medium.classList.add("active");
                strong.classList.add("active");
                text.textContent = "Your password is strong";
                text.classList.add("strong");
            } else {
                strong.classList.remove("active");
                text.classList.remove("strong");
            }
        } else {
            indicator.style.display = "none";
            text.style.display = "none";
        }
    }

    function validateEmail(emailText) {
        const re = /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@rvce.edu.in$/;
        return re.test(String(emailText).toLowerCase());
    }
    function validateUsn(usnText) {
        const re = /^\d{1}[A-Z]{2}\d{2}[A-Z]{3}\d{3}$/;
        return re.test(String(usnText).toUpperCase());
    }

    function validatePhone(phoneText) {
        const re = /^[\d\.\-]+$/;
        return re.test(String(phoneText));
    }

    function validateName(nameText) {
        const re = /^[a-zA-Z]*$/;
        return re.test(String(nameText));
    }

    Pass.addEventListener('change', trigger);

    RegisterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        NameError.innerHTML = "";
        UsnError.innerHTML = "";
        PhoneError.innerHTML = "";
        EmailError.innerHTML = "";
        PassError.innerHTML = "";
        CPassError.innerHTML = "";

        let valid = true;

        if (!validateName(Name.value)) {
            NameError.innerText = "Please enter a valid name.";
            valid = false;
        }

        if (!validateUsn(Usn.value)) {
            UsnError.innerText = "Please enter a valid USN.";
            valid = false;
        }

        if (!validatePhone(Phone.value)) {
            PhoneError.innerText = "Please enter a valid phone number.";
            valid = false;
        }

        if (!validateEmail(Email.value)) {
            EmailError.innerText = "Please enter a valid email.";
            valid = false;
        }

        if (Pass.value.length < 8) {
            PassError.innerHTML = "Password must be at least 8 characters.";
            valid = false;
        } else if (Pass.value !== CPass.value) {
            CPassError.innerHTML = "Passwords do not match.";
            Pass.value = "";
            CPass.value = "";
            valid = false;
        }

        if (valid) {
            RegisterForm.submit();
        }
    });
});
