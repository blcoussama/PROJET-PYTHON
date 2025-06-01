
    document.querySelectorAll('.btn-unsave').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm('Retirer cet article ?')) return;
            const id = btn.dataset.id;
            const res = await fetch(`/save-article/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            const d = await res.json();
            if (d.success && !d.saved) {
                btn.closest('.article-card').remove();
                if (!document.querySelector('.article-card')) location.reload();
            }
        });
    });
