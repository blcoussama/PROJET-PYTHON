
    document.addEventListener('DOMContentLoaded', () => {
        // Enhanced button interactions
        document.querySelectorAll('.action-btn:not(.disabled)').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-3px)';
            });

            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0)';
            });
        });

        // Scroll progress indicator
        function updateScrollProgress() {
            const contentArea = document.querySelector('.article-content-area');
            const progressBar = document.querySelector('.scroll-progress');

            if (contentArea && progressBar) {
                const scrollTop = contentArea.scrollTop;
                const scrollHeight = contentArea.scrollHeight - contentArea.clientHeight;
                const scrollProgress = (scrollTop / scrollHeight) * 100;

                progressBar.style.width = Math.min(scrollProgress, 100) + '%';
            }
        }

        // Add scroll listener to content area
        const contentArea = document.querySelector('.article-content-area');
        if (contentArea) {
            contentArea.addEventListener('scroll', updateScrollProgress);
        }

        // Also listen to window scroll for mobile
        window.addEventListener('scroll', updateScrollProgress);

        // Smooth scroll for comments
        const commentsSection = document.querySelector('.comments-section');
        if (commentsSection) {
            commentsSection.addEventListener('click', (e) => {
                if (e.target.matches('.comment-input')) {
                    e.target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
        }

        // Enhanced sticky behavior check
        function checkStickySupport() {
            const sidebar = document.querySelector('.sticky-sidebar');
            if (sidebar) {
                // Force repaint to ensure sticky works
                sidebar.style.transform = 'translateZ(0)';
            }
        }

        checkStickySupport();
    });

    function toggleLike(articleId) {
        const btn = document.getElementById('like-btn');
        btn.classList.add('loading');
        btn.disabled = true;

        fetch('/like-article/' + articleId, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('likes-count').textContent = data.likes_count;
                    btn.classList.toggle('active', data.liked);
                } else {
                    alert('Erreur: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur de connexion');
            })
            .finally(() => {
                btn.classList.remove('loading');
                btn.disabled = false;
            });
    }

    function toggleSave(articleId) {
        const btn = document.getElementById('save-btn');
        const txt = document.getElementById('save-text');
        btn.classList.add('loading');
        btn.disabled = true;

        fetch('/save-article/' + articleId, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    btn.classList.toggle('active', data.saved);
                    txt.textContent = data.saved ? 'Sauvegardé' : 'Sauvegarder';
                } else {
                    alert('Erreur: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur de connexion');
            })
            .finally(() => {
                btn.classList.remove('loading');
                btn.disabled = false;
            });
    }

    function deleteArticle(articleId) {
        if (!confirm('Êtes-vous sûr de supprimer cet article ?')) return;

        fetch('/delete-article/' + articleId, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                } else {
                    alert('Erreur: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur de connexion');
            });
    }

    function addComment(event, articleId) {
        event.preventDefault();
        const form = event.target;
        const content = form.content.value.trim();

        if (!content) {
            alert('Veuillez saisir un commentaire');
            return;
        }

        const submitBtn = form.querySelector('.comment-submit');
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        const body = new URLSearchParams({ content });
        fetch('/comment-article/' + articleId, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: body.toString()
        })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur de connexion');
            })
            .finally(() => {
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
            });
    }
