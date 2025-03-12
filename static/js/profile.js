document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profileForm');
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    const currentPassword = document.getElementById('current_password');

    form.addEventListener('submit', function(e) {
        // Reset previous error states
        newPassword.style.borderColor = '';
        confirmPassword.style.borderColor = '';
        
        // Validate if user is trying to change password
        if (newPassword.value || confirmPassword.value) {
            if (!currentPassword.value) {
                e.preventDefault();
                currentPassword.style.borderColor = '#ef4444';
                alert('Please enter your current password to make changes');
                return;
            }

            if (newPassword.value !== confirmPassword.value) {
                e.preventDefault();
                newPassword.style.borderColor = '#ef4444';
                confirmPassword.style.borderColor = '#ef4444';
                alert('New passwords do not match');
                return;
            }
        }

        // If user is making any changes, require current password
        const username = document.getElementById('username');
        if (username.value !== username.defaultValue && !currentPassword.value) {
            e.preventDefault();
            currentPassword.style.borderColor = '#ef4444';
            alert('Please enter your current password to make changes');
            return;
        }
    });

    // Clear error states on input
    [newPassword, confirmPassword, currentPassword].forEach(input => {
        input.addEventListener('input', function() {
            this.style.borderColor = '';
        });
    });
});