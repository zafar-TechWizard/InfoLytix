document.addEventListener('DOMContentLoaded', function() {
    const editProfileBtn = document.getElementById('editProfileBtn');
    const profilePopup = document.getElementById('profilePopup');
    const profileContent = profilePopup.querySelector('.profile-popup-content');
    let isLoading = false;

    // Load profile content with loading state
    async function loadProfileContent() {
        if (isLoading) return;
        
        try {
            isLoading = true;
            profileContent.innerHTML = `
                <div class="flex items-center justify-center h-40">
                    <div class="animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent"></div>
                </div>`;

            const response = await fetch('/profile?popup=true');
            const html = await response.text();
            
            // Fade out current content
            profileContent.style.opacity = '0';
            
            setTimeout(() => {
                profileContent.innerHTML = html;
                profileContent.style.opacity = '1';
                initializeProfileForm();
            }, 300);

        } catch (error) {
            console.error('Error loading profile:', error);
            profileContent.innerHTML = `
                <div class="text-red-500 text-center p-4">
                    <i class="fas fa-exclamation-circle text-2xl mb-2"></i>
                    <p>Error loading profile</p>
                </div>`;
        } finally {
            isLoading = false;
        }
    }

    // Enhanced form initialization
    function initializeProfileForm() {
        const form = profileContent.querySelector('#profileForm');
        if (!form) return;

        const inputs = form.querySelectorAll('input');
        const submitBtn = form.querySelector('.save-btn');

        // Add floating labels effect
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                if (!input.value) {
                    input.parentElement.classList.remove('focused');
                }
            });
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <div class="flex items-center justify-center">
                    <div class="animate-spin h-4 w-4 border-2 border-white rounded-full border-t-transparent mr-2"></div>
                    Saving...
                </div>`;
            
            try {
                const formData = new FormData(form);
                const response = await fetch('/profile', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.text();
                profileContent.innerHTML = result;
                initializeProfileForm();
                
            } catch (error) {
                console.error('Error updating profile:', error);
                submitBtn.innerHTML = 'Save Changes';
                submitBtn.disabled = false;
            }
        });
    }

    // Show profile popup with fade effect
    editProfileBtn.addEventListener('click', (e) => {
        e.preventDefault();
        document.body.style.overflow = 'hidden';
        profilePopup.classList.add('show');
        loadProfileContent();
    });

    // Close popup handlers
    function closePopup() {
        document.body.style.overflow = '';
        profilePopup.classList.remove('show');
        setTimeout(() => {
            profileContent.innerHTML = '';
        }, 300);
    }

    profilePopup.addEventListener('click', (e) => {
        if (e.target === profilePopup) {
            closePopup();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && profilePopup.classList.contains('show')) {
            closePopup();
        }
    });
});