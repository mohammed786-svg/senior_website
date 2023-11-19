document.addEventListener('DOMContentLoaded', function () {
    const passwordField = document.getElementById('passwrd');
    const showPasswordToggle = document.getElementById('showPasswordToggle');
    const showIcon = showPasswordToggle.querySelector('.fa-eye');
    const hideIcon = showPasswordToggle.querySelector('.fa-eye-slash');

    showPasswordToggle.addEventListener('click', function () {
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            showIcon.style.display = 'none';
            hideIcon.style.display = 'block';
        } else {
            passwordField.type = 'password';
            showIcon.style.display = 'block';
            hideIcon.style.display = 'none';
        }
    });
});

//Calculate Age when dob is selected
document.addEventListener('DOMContentLoaded', function () {
    // Get references to the date of birth and age input fields
    const dateOfBirthInput = document.getElementById('date-of-birth');
    const ageInput = document.getElementById('input-age');

    // Attach an event listener to the date of birth input field
    dateOfBirthInput.addEventListener('input', function () {
        // Get the selected date of birth
        const dateOfBirth = new Date(dateOfBirthInput.value);

        // Calculate the age
        const today = new Date();
        const age = today.getFullYear() - dateOfBirth.getFullYear();

        // Update the age input field with the calculated age
        ageInput.value = age;
    });
});

/* 1. Proloder */
$(window).on('load', function () {
    $('#preloader-active').delay(450).fadeOut('slow');
    $('body').delay(450).css({
      'overflow': 'visible'
    });
  });
  