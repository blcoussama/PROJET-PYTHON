
    function deleteArticle(articleId) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet article ?')) {
            return;
        }

        fetch('/delete-article/' + articleId, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Retirer la carte correspondante du DOM
                    const card = document.querySelector(`.article-card[data-article-id="${articleId}"]`);
                    if (card) {
                        card.remove();
                    }
                    // Si plus aucune carte, recharger pour afficher l'empty-state
                    if (!document.querySelector('.article-card')) {
                        window.location.reload();
                    }
                } else {
                    alert('Erreur : ' + (data.error || 'Impossible de supprimer l\'article.'));
                }
            })
            .catch(err => {
                console.error('Erreur lors de la requête :', err);
                alert('Impossible de joindre le serveur.');
            });
    }
