document.addEventListener('DOMContentLoaded', function () {
    var navToggle = document.querySelector('.nav-toggle');
    var navMenu = document.getElementById('nav-menu');
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('open');
        });
    }

    function closeDropdowns() {
        document.querySelectorAll('.dropdown.open').forEach(function (item) {
            item.classList.remove('open');
        });
    }

    document.querySelectorAll('[data-dropdown]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            var parent = btn.closest('.dropdown');
            var wasOpen = parent.classList.contains('open');
            closeDropdowns();
            if (!wasOpen) {
                parent.classList.add('open');
                btn.setAttribute('aria-expanded', 'true');
            } else {
                btn.removeAttribute('aria-expanded');
            }
        });
    });

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.dropdown')) {
            closeDropdowns();
        }
    });

    document.querySelectorAll('.flash-close').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var flash = btn.closest('.flash');
            if (flash) { flash.remove(); }
        });
    });

    function openModal(modal) {
        if (!modal) { return; }
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modal) {
        if (!modal) { return; }
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }

    document.querySelectorAll('[data-open-modal]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            openModal(document.getElementById(btn.getAttribute('data-open-modal')));
        });
    });

    document.querySelectorAll('[data-close-modal]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var modal = btn.closest('.modal-overlay');
            closeModal(modal);
        });
    });

    document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) {
                closeModal(overlay);
            }
        });
    });

    var authForm = document.getElementById('authForm');
    var nextBtn = document.getElementById('nextBtn');
    if (authForm && nextBtn) {
        function refreshNext() {
            if (authForm.checkValidity()) {
                nextBtn.classList.add('valid');
                nextBtn.disabled = false;
            } else {
                nextBtn.classList.remove('valid');
                nextBtn.disabled = true;
            }
        }
        authForm.addEventListener('input', refreshNext);
        authForm.addEventListener('change', refreshNext);
        refreshNext();
    }

    var drawerClose = document.querySelector('[data-drawer-close]');
    var drawerBackdrop = document.querySelector('.drawer-backdrop');
    if (drawerClose && drawerBackdrop) {
        function hideDrawer() {
            var drawer = document.querySelector('.cart-drawer');
            if (drawer) { drawer.style.display = 'none'; }
            drawerBackdrop.style.display = 'none';
        }
        drawerClose.addEventListener('click', hideDrawer);
        drawerBackdrop.addEventListener('click', hideDrawer);
    }

    function setupCarousel(carousel) {
        if (!carousel) { return; }
        var track = carousel.querySelector('.carousel-track');
        var prev = carousel.querySelector('.prev');
        var next = carousel.querySelector('.next');
        if (!track || !prev || !next) { return; }

        function updateArrows() {
            prev.disabled = track.scrollLeft <= 4;
            next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 4;
        }

        next.addEventListener('click', function () {
            track.scrollBy({ left: track.clientWidth * .8, behavior: 'smooth' });
        });

        prev.addEventListener('click', function () {
            track.scrollBy({ left: -track.clientWidth * .8, behavior: 'smooth' });
        });

        track.addEventListener('scroll', updateArrows);
        updateArrows();
    }

    setupCarousel(document.querySelector('.carousel'));

    var searchInput = document.getElementById('globalSearch');

    function filterCards() {
        var value = (searchInput ? searchInput.value : '').toLowerCase().trim();
        document.querySelectorAll('.oc-card').forEach(function (card) {
            var text = card.textContent.toLowerCase();
            card.style.display = text.indexOf(value) !== -1 ? '' : 'none';
        });
    }

    function isTiendaPage() {
        return window.location.pathname.indexOf('/tienda') !== -1;
    }

    if (searchInput) {
        if (isTiendaPage() && sessionStorage.getItem('oxxo_search')) {
            searchInput.value = sessionStorage.getItem('oxxo_search');
            filterCards();
        }

        searchInput.addEventListener('input', function () {
            sessionStorage.setItem('oxxo_search', searchInput.value);
            filterCards();
        });

        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !isTiendaPage()) {
                sessionStorage.setItem('oxxo_search', searchInput.value);
                window.location.href = '/tienda/';
            }
        });
    }
});