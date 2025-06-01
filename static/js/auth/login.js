
    // Enhanced form handling
    document.getElementById('loginForm').addEventListener('submit', function (e) {
      const submitBtn = document.getElementById('submitBtn');
      submitBtn.classList.add('loading');
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connexion...';
    });

    // Form validation feedback
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
      input.addEventListener('blur', function () {
        if (this.checkValidity()) {
          this.style.borderColor = 'var(--success-color)';
        } else {
          this.style.borderColor = 'var(--danger-color)';
        }
      });

      input.addEventListener('focus', function () {
        this.style.borderColor = 'var(--primary-color)';
      });
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