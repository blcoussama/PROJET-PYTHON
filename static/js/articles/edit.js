
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('editForm');
    const submitBtn = document.getElementById('submitBtn');
    const removeCurrentImageBtn = document.getElementById('removeCurrentImage');
    const currentImageContainer = document.getElementById('currentImageContainer');
    const imageRemovalNotice = document.getElementById('imageRemovalNotice');
    const undoImageRemovalBtn = document.getElementById('undoImageRemoval');
    const removeImageField = document.getElementById('remove_image');

    // Character counters
    const counters = [
        { input: 'title', counter: 'titleCounter', max: 200 },
        { input: 'description', counter: 'descCounter', max: 500 },
        { input: 'content', counter: 'contentCounter', max: 10000 }
    ];

    counters.forEach(({ input, counter, max }) => {
        const inputEl = document.getElementById(input);
        const counterEl = document.getElementById(counter);

        // Initialize counter with current content
        const currentLength = inputEl.value.length;
        counterEl.textContent = `${currentLength}/${max}`;
        
        // Update counter styling based on current length
        counterEl.className = 'char-counter';
        if (currentLength > max * 0.8) {
            counterEl.classList.add('warning');
        }
        if (currentLength > max * 0.95) {
            counterEl.classList.add('danger');
        }

        inputEl.addEventListener('input', function() {
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

    // Image removal functionality
    if (removeCurrentImageBtn) {
        removeCurrentImageBtn.addEventListener('click', function() {
            if (confirm('Êtes-vous sûr de vouloir supprimer l\'image actuelle ?')) {
                currentImageContainer.style.opacity = '0.5';
                imageRemovalNotice.classList.add('show');
                removeImageField.value = 'true';
                this.disabled = true;
                this.textContent = 'Image marquée pour suppression';
            }
        });
    }

    if (undoImageRemovalBtn) {
        undoImageRemovalBtn.addEventListener('click', function() {
            currentImageContainer.style.opacity = '1';
            imageRemovalNotice.classList.remove('show');
            removeImageField.value = 'false';
            if (removeCurrentImageBtn) {
                removeCurrentImageBtn.disabled = false;
                removeCurrentImageBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Supprimer l\'image';
            }
        });
    }

    // File input validation
    const fileInput = document.getElementById('image');
    fileInput.addEventListener('change', function(e) {
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

            // If a new file is selected, cancel image removal
            if (removeImageField.value === 'true') {
                removeImageField.value = 'false';
                imageRemovalNotice.classList.remove('show');
                if (currentImageContainer) {
                    currentImageContainer.style.opacity = '1';
                }
                if (removeCurrentImageBtn) {
                    removeCurrentImageBtn.disabled = false;
                    removeCurrentImageBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Supprimer l\'image';
                }
            }
        }
    });

    // Form submission (preserved original functionality with enhanced UX)
    form.addEventListener('submit', function(e) {
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
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enregistrement en cours...';
        submitBtn.disabled = true;
    });

    // Auto-save to localStorage for edit mode
    const autoSaveFields = ['title', 'description', 'content'];
    const articleId = '{{ article.id }}';
    
    autoSaveFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        
        // Load saved data specific to this article
        const savedValue = localStorage.getItem(`edit_article_${articleId}_${fieldId}`);
        if (savedValue && savedValue !== field.value) {
            // Show option to restore saved changes
            if (confirm(`Des modifications non sauvegardées ont été trouvées pour le champ "${fieldId}". Voulez-vous les restaurer ?`)) {
                field.value = savedValue;
                field.dispatchEvent(new Event('input'));
            }
        }

        // Save on input
        field.addEventListener('input', function() {
            localStorage.setItem(`edit_article_${articleId}_${fieldId}`, this.value);
        });
    });

    // Clear auto-save on successful submission
    form.addEventListener('submit', function() {
        setTimeout(() => {
            autoSaveFields.forEach(fieldId => {
                localStorage.removeItem(`edit_article_${articleId}_${fieldId}`);
            });
        }, 1000);
    });

    // Form validation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            const formGroup = this.closest('.form-group');
            formGroup.classList.remove('has-error', 'has-success');
            
            if (this.checkValidity() && this.value.trim()) {
                formGroup.classList.add('has-success');
            } else if (!this.checkValidity()) {
                formGroup.classList.add('has-error');
            }
        });

        input.addEventListener('focus', function() {
            const formGroup = this.closest('.form-group');
            formGroup.classList.remove('has-error', 'has-success');
        });
    });
});