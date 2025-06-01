        // Form validation and enhancement
        const form = document.getElementById('registerForm');
        const usernameInput = document.getElementById('username');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        const submitBtn = document.getElementById('submitBtn');

        // Validation state
        const validationState = {
            username: false,
            email: false,
            password: false,
            confirmPassword: false
        };

        // Username validation
        usernameInput.addEventListener('input', function () {
            const value = this.value.trim();
            const validation = document.getElementById('usernameValidation');

            if (value.length < 3) {
                showValidation(this, validation, false, 'Le nom d\'utilisateur doit contenir au moins 3 caractères');
                validationState.username = false;
            } else if (value.length > 20) {
                showValidation(this, validation, false, 'Le nom d\'utilisateur ne peut pas dépasser 20 caractères');
                validationState.username = false;
            } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
                showValidation(this, validation, false, 'Seules les lettres, chiffres et underscores sont autorisés');
                validationState.username = false;
            } else {
                showValidation(this, validation, true, 'Nom d\'utilisateur valide');
                validationState.username = true;
            }
            updateSubmitButton();
        });

        // Email validation
        emailInput.addEventListener('input', function () {
            const value = this.value.trim();
            const validation = document.getElementById('emailValidation');
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!emailRegex.test(value)) {
                showValidation(this, validation, false, 'Veuillez entrer une adresse email valide');
                validationState.email = false;
            } else {
                showValidation(this, validation, true, 'Adresse email valide');
                validationState.email = true;
            }
            updateSubmitButton();
        });

        // Password strength validation
        passwordInput.addEventListener('input', function () {
            const value = this.value;
            const strength = calculatePasswordStrength(value);
            const strengthIndicator = document.getElementById('strengthIndicator');
            const strengthMessage = document.getElementById('passwordStrength');

            updateStrengthIndicator(strengthIndicator, strength);

            if (value.length < 8) {
                showValidation(this, strengthMessage, false, 'Le mot de passe doit contenir au moins 8 caractères');
                validationState.password = false;
            } else if (strength.score < 2) {
                showValidation(this, strengthMessage, false, 'Mot de passe trop faible');
                validationState.password = false;
            } else {
                showValidation(this, strengthMessage, true, strength.feedback);
                validationState.password = true;
            }

            // Re-validate confirm password if it has content
            if (confirmPasswordInput.value) {
                confirmPasswordInput.dispatchEvent(new Event('input'));
            }

            updateSubmitButton();
        });

        // Confirm password validation
        confirmPasswordInput.addEventListener('input', function () {
            const value = this.value;
            const passwordValue = passwordInput.value;
            const matchIndicator = document.getElementById('passwordMatch');

            if (value === '') {
                matchIndicator.innerHTML = '';
                matchIndicator.className = 'password-match';
                validationState.confirmPassword = false;
            } else if (value === passwordValue) {
                matchIndicator.innerHTML = '<i class="fas fa-check"></i> Les mots de passe correspondent';
                matchIndicator.className = 'password-match match';
                validationState.confirmPassword = true;
            } else {
                matchIndicator.innerHTML = '<i class="fas fa-times"></i> Les mots de passe ne correspondent pas';
                matchIndicator.className = 'password-match no-match';
                validationState.confirmPassword = false;
            }
            updateSubmitButton();
        });

        // Calculate password strength
        function calculatePasswordStrength(password) {
            let score = 0;
            const feedback = [];

            if (password.length >= 8) score++;
            if (password.length >= 12) score++;
            if (/[a-z]/.test(password)) score++;
            if (/[A-Z]/.test(password)) score++;
            if (/[0-9]/.test(password)) score++;
            if (/[^A-Za-z0-9]/.test(password)) score++;

            let strength = 'Très faible';
            if (score >= 6) strength = 'Très fort';
            else if (score >= 4) strength = 'Fort';
            else if (score >= 3) strength = 'Moyen';
            else if (score >= 2) strength = 'Faible';

            return {
                score: Math.min(score, 4),
                feedback: `Force du mot de passe: ${strength}`
            };
        }

        // Update strength indicator bars
        function updateStrengthIndicator(indicator, strength) {
            const bars = indicator.querySelectorAll('.strength-bar');
            bars.forEach((bar, index) => {
                bar.className = 'strength-bar';
                if (index < strength.score) {
                    bar.classList.add('active');
                    if (strength.score <= 1) bar.classList.add('weak');
                    else if (strength.score <= 2) bar.classList.add('medium');
                    else bar.classList.add('strong');
                }
            });
        }

        // Show validation message
        function showValidation(input, messageElement, isValid, message) {
            input.className = `form-control ${isValid ? 'valid' : 'invalid'}`;
            messageElement.className = `validation-message ${isValid ? 'success' : 'error'}`;
            messageElement.innerHTML = `<i class="fas fa-${isValid ? 'check' : 'times'}"></i> ${message}`;
        }

        // Update submit button state
        function updateSubmitButton() {
            const allValid = Object.values(validationState).every(state => state);
            submitBtn.disabled = !allValid;
        }

        // Form submission
        form.addEventListener('submit', function (e) {
            submitBtn.classList.add('loading');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Création du compte...';
        });

        // Auto-dismiss alerts
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%)';
                setTimeout(() => alert.remove(), 300);
            });
        }, 5000);