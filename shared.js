(function () {
    const path = window.location.pathname;

    function isActive(href) {
        if (href === '/pool-database') return path === '/pool-database' || path.startsWith('/pool-database/');
        return path === href || path === href.replace(/\.html$/, '');
    }

    function a(href, label, cls) {
        const active = isActive(href);
        const classes = [cls, active ? 'active' : ''].filter(Boolean).join(' ');
        return '<a href="' + href + '"' + (classes ? ' class="' + classes + '"' : '') + '>' + label + '</a>';
    }

    const nav = document.querySelector('nav');
    if (nav) {
        nav.innerHTML =
            '<a href="/index.html" class="logo">DYKE POOL DB</a>' +
            '<ul class="nav-links">' +
            '<li>' + a('/pool-database', 'Database') + '</li>' +
            '<li class="hide">' + a('/stats.html', 'Stats') + '</li>' +
            '<li class="hide">' + a('/about.html', 'About') + '</li>' +
            '<li>' + a('/submit', 'Contribute', 'pill') + '</li>' +
            '</ul>';
    }

    const footer = document.querySelector('footer');
    if (footer) {
        footer.innerHTML =
            '<div class="footer-logo">DYKE POOL DB</div>' +
            '<div class="footer-right">' +
            '<a href="https://www.dykepool.com" target="_blank">Dyke Pool Website</a>' +
            '<span class="footer-sep">·</span>' +
            '<a href="https://github.com/dykepooldb/" target="_blank">GitHub</a>' +
            '<span class="footer-sep">·</span>' +
            '<span>© 2026 homoveralls</span>' +
            '</div>';
    }
})();
