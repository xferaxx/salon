document.addEventListener("DOMContentLoaded", function () {
    // Form validation for registration
    const registerForm = document.querySelector("#registerForm");  // Updated to be more specific
    if (registerForm) {
        registerForm.addEventListener("submit", function (event) {
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            const email = document.getElementById("email").value.trim();
            const role = document.getElementById("role").value;

            let errorMessages = [];

            // Check if all fields are filled
            if (!username || !password || !email || !role) {
                errorMessages.push("Please fill out all fields.");
            }

            // Simple email format validation
            const emailPattern = /^[^@]+@\w+(\.\w+)+\w$/;
            if (!emailPattern.test(email)) {
                errorMessages.push("Please enter a valid email address.");
            }

            // Password length validation
            if (password.length < 6) {
                errorMessages.push("Password must be at least 6 characters long.");
            }

            // If there are any errors, display alert and prevent form submission
            if (errorMessages.length > 0) {
                alert(errorMessages.join("\n"));
                event.preventDefault();  // Prevent form submission
            }
        });
    }

    // Date picker for appointment booking
    const appointmentDateInput = document.querySelector("input[type='datetime-local']");
    if (appointmentDateInput) {
        const today = new Date().toISOString().split('T')[0];
        appointmentDateInput.setAttribute('min', today); // Disable past dates
    }

    // Form validation for appointment booking
    const appointmentForm = document.querySelector("#appointmentForm");
    if (appointmentForm) {
        appointmentForm.addEventListener("submit", function (event) {
            const appointmentDate = document.getElementById("appointment_date").value;
            const selectedService = document.getElementById("service").value;

            let errorMessages = [];

            // Check if both date and service are selected
            if (!appointmentDate) {
                errorMessages.push("Please select a valid date.");
            }

            if (!selectedService) {
                errorMessages.push("Please select a service.");
            }

            // If there are any errors, display alert and prevent form submission
            if (errorMessages.length > 0) {
                alert(errorMessages.join("\n"));
                event.preventDefault();  // Prevent form submission
            }
        });
    }

    // Tooltip logic for calendar events (Hover over appointments to see full details)
    document.querySelectorAll('.fc-event').forEach(event => {
        event.addEventListener('mouseenter', function(e) {
            const title = e.target.querySelector('.fc-event-title').textContent;
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = title;
            document.body.appendChild(tooltip);

            tooltip.style.left = e.pageX + 'px';
            tooltip.style.top = e.pageY + 'px';
        });

        event.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
});
