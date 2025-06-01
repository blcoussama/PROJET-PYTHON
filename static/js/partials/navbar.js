    // Mobile menu toggle
    const navToggle = document.getElementById("navToggle");
    const navMenu = document.getElementById("navMenu");

    navToggle.addEventListener("click", () => {
        navMenu.classList.toggle("active");
        navToggle.classList.toggle("active");
    });

    // Close mobile menu on link click
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove("active");
            navToggle.classList.remove("active");
        });
    });

    // User dropdown functionality
    const userDropdown = document.getElementById("userDropdown");
    if (userDropdown) {
        const dropdownBtn = userDropdown.querySelector(".nav-dropdown-btn");

        dropdownBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle("open");
        });

        document.addEventListener("click", (e) => {
            if (!userDropdown.contains(e.target)) {
                userDropdown.classList.remove("open");
            }
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                userDropdown.classList.remove("open");
            }
        });
    }