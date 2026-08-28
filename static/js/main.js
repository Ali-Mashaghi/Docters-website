(function () {
    'use strict';

    const THEME_KEY = 'doctor-platform-theme';

    function initTheme() {
        const saved = localStorage.getItem(THEME_KEY);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = saved || (prefersDark ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', theme);
        updateThemeIcon(theme);
    }

    function updateThemeIcon(theme) {
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.textContent = theme === 'dark' ? '☀️' : '🌙';
            btn.setAttribute('aria-label', theme === 'dark' ? 'حالت روشن' : 'حالت تاریک');
        }
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem(THEME_KEY, next);
        updateThemeIcon(next);
    }

    function initMobileNav() {
        const hamburger = document.getElementById('hamburger');
        const navLinks = document.getElementById('nav-links');

        if (!hamburger || !navLinks) return;

        hamburger.addEventListener('click', function () {
            navLinks.classList.toggle('open');
            hamburger.classList.toggle('active');
        });

        navLinks.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                navLinks.classList.remove('open');
                hamburger.classList.remove('active');
            });
        });
    }

    function initPortfolioLightbox() {
        const items = document.querySelectorAll('.portfolio-item');
        items.forEach(function (item) {
            item.addEventListener('click', function () {
                const img = item.querySelector('img');
                if (!img) return;

                const overlay = document.createElement('div');
                overlay.style.cssText = [
                    'position:fixed', 'inset:0', 'z-index:9999',
                    'background:rgba(0,0,0,0.8)', 'backdrop-filter:blur(8px)',
                    'display:flex', 'align-items:center', 'justify-content:center',
                    'cursor:pointer', 'padding:1rem',
                ].join(';');

                const enlarged = document.createElement('img');
                enlarged.src = img.src;
                enlarged.alt = img.alt;
                enlarged.style.cssText = 'max-width:90%;max-height:90%;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.5);';

                overlay.appendChild(enlarged);
                document.body.appendChild(overlay);

                overlay.addEventListener('click', function () {
                    overlay.remove();
                });
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initTheme();
        initMobileNav();
        initPortfolioLightbox();

        const themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) {
            themeBtn.addEventListener('click', toggleTheme);
        }
    });
})();
