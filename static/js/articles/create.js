document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('articleForm');
    const submitBtn = document.getElementById('submitBtn');
    const fileInput = document.getElementById('image');
    const fileLabel = document.getElementById('fileLabel');
    const filePreview = document.getElementById('filePreview');
    const previewImage = document.getElementById('previewImage');
    const fileName = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFile');
    const draftBanner = document.getElementById('draftBanner');
    const restoreDraftBtn = document.getElementById('restoreDraft');
    const dismissDraftBtn = document.getElementById('dismissDraft');
    const autoSaveNotification = document.getElementById('autoSaveNotification');

    // Character counters
    const counters = [
        { input: 'title', counter: 'titleCounter', max: 200 },
        { input: 'description', counter: 'descCounter', max: 500 },
        { input: 'content', counter: 'contentCounter', max: 10000 }
    ];

    counters.forEach(({ input, counter, max }) => {
        const inputEl = document.getElementById(input);
        const counterEl = document.getElementById(counter);

        inputEl.addEventListener('input', function () {
            const length = this.value.length;
            counterEl.textContent = `${length}/${max}`;

            counterEl.className = 'char-counter';
            if (length > max * 0.8) {
                counterEl.classList.add('warning');
            }
            if (length > max * 0.95) {
                counterEl.classList.add('danger');
            }
        });
    });

    // File upload handling (enhanced functionality)
    fileInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
            if (!validTypes.includes(file.type)) {
                alert('Veuillez sélectionner un fichier PNG, JPG ou JPEG.');
                this.value = '';
                return;
            }

            // Validate file size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                alert('La taille du fichier ne doit pas dépasser 5MB.');
                this.value = '';
                return;
            }

            // Update label
            fileLabel.classList.add('has-file');
            fileLabel.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>Image sélectionnée: ${file.name}</span>
        `;

            // Show preview
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImage.src = e.target.result;
                fileName.textContent = `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
                filePreview.classList.add('show');
            };
            reader.readAsDataURL(file);
        }
    });

    // Remove file
    removeFileBtn.addEventListener('click', function () {
        fileInput.value = '';
        fileLabel.classList.remove('has-file');
        fileLabel.innerHTML = `
        <i class="fas fa-cloud-upload-alt"></i>
        <span>Cliquez pour sélectionner une image ou glissez-déposez</span>
    `;
        filePreview.classList.remove('show');
    });

    // Drag and drop functionality
    fileLabel.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.style.borderColor = 'var(--primary-color)';
        this.style.background = 'rgba(0, 123, 255, 0.1)';
    });

    fileLabel.addEventListener('dragleave', function (e) {
        e.preventDefault();
        this.style.borderColor = 'var(--border-color)';
        this.style.background = '#f8f9fa';
    });

    fileLabel.addEventListener('drop', function (e) {
        e.preventDefault();
        this.style.borderColor = 'var(--border-color)';
        this.style.background = '#f8f9fa';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });

    // Form validation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function () {
            const formGroup = this.closest('.form-group');
            formGroup.classList.remove('has-error', 'has-success');

            if (this.checkValidity() && this.value.trim()) {
                formGroup.classList.add('has-success');
            } else if (!this.checkValidity()) {
                formGroup.classList.add('has-error');
            }
        });

        input.addEventListener('focus', function () {
            const formGroup = this.closest('.form-group');
            formGroup.classList.remove('has-error', 'has-success');
        });
    });

    // Form submission (preserved original functionality with enhanced UX)
    form.addEventListener('submit', function (e) {
        // Validate required fields
        const title = document.getElementById('title').value.trim();
        const content = document.getElementById('content').value.trim();

        if (!title || !content) {
            e.preventDefault();
            alert('Veuillez remplir tous les champs obligatoires.');
            return;
        }

        // Show loading state
        submitBtn.classList.add('loading');
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publication en cours...';
        submitBtn.disabled = true;

        // Clear auto-save data immediately on successful submission
        clearDraftData();
    });

    // Auto-save functionality (CORRECTED - no automatic restoration)
    const autoSaveFields = ['title', 'description', 'content'];
    let autoSaveTimeout;

    function showAutoSaveNotification() {
        autoSaveNotification.classList.add('show');
        setTimeout(() => {
            autoSaveNotification.classList.remove('show');
        }, 2000);
    }

    function checkForDraft() {
        const hasDraft = autoSaveFields.some(fieldId => {
            const savedValue = localStorage.getItem(`article_draft_${fieldId}`);
            return savedValue && savedValue.trim() !== '';
        });

        if (hasDraft) {
            draftBanner.style.display = 'flex';
        }
    }

    function restoreDraft() {
        autoSaveFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            const savedValue = localStorage.getItem(`article_draft_${fieldId}`);
            if (savedValue) {
                field.value = savedValue;
                field.dispatchEvent(new Event('input'));
            }
        });
        draftBanner.style.display = 'none';
    }

    function clearDraftData() {
        autoSaveFields.forEach(fieldId => {
            localStorage.removeItem(`article_draft_${fieldId}`);
        });
        draftBanner.style.display = 'none';
    }

    // Auto-save on input with debouncing
    autoSaveFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);

        field.addEventListener('input', function () {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                if (this.value.trim()) {
                    localStorage.setItem(`article_draft_${fieldId}`, this.value);
                    showAutoSaveNotification();
                } else {
                    localStorage.removeItem(`article_draft_${fieldId}`);
                }
            }, 1000); // Save after 1 second of inactivity
        });
    });

    // Draft banner event listeners
    restoreDraftBtn.addEventListener('click', restoreDraft);
    dismissDraftBtn.addEventListener('click', clearDraftData);

    // Check for existing draft on page load
    checkForDraft();

    // Clear draft data when leaving the page after successful submission
    window.addEventListener('beforeunload', function () {
        // Only clear if form was submitted successfully
        if (submitBtn.classList.contains('loading')) {
            clearDraftData();
        }
    });
});