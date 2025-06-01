
    document.querySelectorAll('.btn-unlike').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm('Retirer cet article des articles aimés ?')) return;
            const articleId = btn.dataset.id;

            try {
                const response = await fetch(`/like-article/${articleId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                });
                const result = await response.json();

                if (result.success && !result.liked) {
                    // Remove this card from the DOM
                    const card = document.querySelector(`.article-card[data-article-id="${articleId}"]`);
                    if (card) card.remove();

                    // If no more cards remain, reload to show empty state
                    if (!document.querySelector('.article-card')) {
                        location.reload();
                    }
                } else {
                    alert('Erreur : ' + (result.error || 'Impossible de retirer le like.'));
                }
            } catch (err) {
                console.error('Erreur de réseau :', err);
                alert('Impossible de joindre le serveur.');
            }
        });
    });
