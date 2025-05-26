document.addEventListener("DOMContentLoaded", () => {
    const navToggle = document.getElementById("navToggle");
    const navMenu = document.getElementById("navMenu");

    if (navToggle) {
        navToggle.addEventListener("click", () => {
            navMenu.classList.toggle("active");
        });
    }

    document.querySelectorAll(".btn-like").forEach(btn => {
        btn.addEventListener("click", () => {
            const articleId = btn.dataset.id;
            fetch(`/like-article/${articleId}`, {
                method: "POST"
            }).then(response => {
                if (response.ok) {
                    // Optionally update like count here
                    location.reload();
                }
            });
        });
    });

    document.querySelectorAll(".btn-save").forEach(btn => {
        btn.addEventListener("click", () => {
            const articleId = btn.dataset.id;
            fetch(`/save-article/${articleId}`, {
                method: "POST"
            }).then(response => {
                if (response.ok) {
                    // Optionally update save icon
                    location.reload();
                }
            });
        });
    });

    const dropdownBtn = document.querySelector('.nav-dropdown-btn');
    const dropdown = document.querySelector('.nav-dropdown');

    if (dropdownBtn && dropdown) {
        dropdownBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        // Fermer le dropdown quand on clique ailleurs
        document.addEventListener('click', function (e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });
    }
});
