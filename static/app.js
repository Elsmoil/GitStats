/* ============================================================
   GitStats – app.js
   Handles: theme toggle, URL validation, loading overlay,
            animated counters, Chart.js contributor chart.
   ============================================================ */

(function () {
    'use strict';

    /* ----------------------------------------------------------
       1. THEME  (dark / light)
    ---------------------------------------------------------- */
    const html        = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon   = document.getElementById('themeIcon');

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        if (themeIcon) {
            themeIcon.className = theme === 'dark'
                ? 'fa-solid fa-moon'
                : 'fa-solid fa-sun';
        }
        try { localStorage.setItem('gs-theme', theme); } catch (_) {}
    }

    // Restore saved preference (default: dark)
    const savedTheme = (() => {
        try { return localStorage.getItem('gs-theme'); } catch (_) { return null; }
    })();
    applyTheme(savedTheme || 'dark');

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            applyTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
        });
    }

    /* ----------------------------------------------------------
       2. URL VALIDATION  (live feedback)
    ---------------------------------------------------------- */
    const GITHUB_RE = /^https:\/\/github\.com\/[A-Za-z0-9][A-Za-z0-9_-]*\/[A-Za-z0-9_][A-Za-z0-9_.\-]*(\.git)?$/;

    const urlInput = document.getElementById('repo_url');
    const urlHint  = document.getElementById('urlHint');

    function isValidGithubUrl(raw) {
        // GITHUB_RE already ensures scheme + domain are correct so URL() will not throw
        if (!GITHUB_RE.test(raw)) return false;
        const parsed = new URL(raw);
        // Pathname must be exactly /<owner>/<repo> (2 non-empty segments)
        const parts = parsed.pathname.split('/').filter(Boolean);
        return parts.length === 2;
    }

    function setInputState(state, msg) {
        if (!urlInput || !urlHint) return;
        urlInput.classList.remove('input-valid', 'input-invalid');
        urlHint.classList.remove('hint-success', 'hint-error');

        if (state === 'valid') {
            urlInput.classList.add('input-valid');
            urlHint.classList.add('hint-success');
            urlHint.textContent = '✓ Valid GitHub repository URL';
        } else if (state === 'invalid') {
            urlInput.classList.add('input-invalid');
            urlHint.classList.add('hint-error');
            urlHint.textContent = msg || 'Please enter a valid https://github.com/owner/repo URL';
        } else {
            urlHint.textContent = 'Enter a public GitHub URL, e.g. https://github.com/torvalds/linux';
        }
    }

    if (urlInput) {
        urlInput.addEventListener('input', () => {
            const val = urlInput.value.trim();
            if (!val) {
                setInputState('neutral');
                return;
            }
            setInputState(isValidGithubUrl(val) ? 'valid' : 'invalid');
        });

        // Run once on load if the field is pre-filled (e.g. after error re-render)
        if (urlInput.value.trim()) {
            urlInput.dispatchEvent(new Event('input'));
        }
    }

    /* ----------------------------------------------------------
       3. FORM SUBMISSION  – show loading overlay
    ---------------------------------------------------------- */
    const form    = document.getElementById('analyzeForm');
    const overlay = document.getElementById('loadingOverlay');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (form) {
        form.addEventListener('submit', (e) => {
            const val = urlInput ? urlInput.value.trim() : '';

            if (!val) {
                e.preventDefault();
                setInputState('invalid', 'Please enter a repository URL before analyzing.');
                urlInput && urlInput.focus();
                return;
            }

            if (!isValidGithubUrl(val)) {
                e.preventDefault();
                setInputState('invalid');
                urlInput && urlInput.focus();
                return;
            }

            // Show loading state
            if (overlay)     overlay.classList.add('active');
            if (analyzeBtn)  analyzeBtn.disabled = true;
        });
    }

    /* ----------------------------------------------------------
       4. ANIMATED COUNTERS
    ---------------------------------------------------------- */
    function animateCounter(el, target, duration) {
        const start = performance.now();
        const step  = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            // ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(eased * target).toLocaleString();
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    }

    document.querySelectorAll('[data-counter]').forEach((el) => {
        const target = parseInt(el.dataset.counter, 10);
        if (!isNaN(target)) el.dataset.counterTarget = target;
    });

    // Single shared IntersectionObserver for all counter elements
    const counterEls = Array.from(document.querySelectorAll('[data-counter-target]'));
    if (counterEls.length) {
        const counterIO = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const target = parseInt(el.dataset.counterTarget, 10);
                    animateCounter(el, target, 900);
                    counterIO.unobserve(el);
                }
            });
        }, { threshold: 0.3 });
        counterEls.forEach((el) => counterIO.observe(el));
    }

    /* ----------------------------------------------------------
       5. CHART.JS  – Commits by Contributor
    ---------------------------------------------------------- */
    const chartCanvas = document.getElementById('contributorsChart');

    if (chartCanvas && window.__REPO_DATA__) {
        const { contributors, commitCounts } = window.__REPO_DATA__;

        // Sort by count descending
        const sorted = contributors
            .map((name) => ({ name, count: commitCounts[name] || 0 }))
            .sort((a, b) => b.count - a.count);

        const labels = sorted.map((d) => d.name);
        const counts = sorted.map((d) => d.count);

        // Theme-aware colours
        function getThemeColors() {
            const isDark = html.getAttribute('data-theme') === 'dark';
            return {
                gridColor:  isDark ? 'rgba(255,255,255,.08)' : 'rgba(0,0,0,.06)',
                labelColor: isDark ? '#94a3b8' : '#64748b',
                tooltipBg:  isDark ? '#1e293b' : '#ffffff',
                tooltipFg:  isDark ? '#f1f5f9' : '#0f172a',
            };
        }

        const PALETTE = [
            '#6366f1','#06b6d4','#10b981','#f59e0b',
            '#ef4444','#8b5cf6','#ec4899','#14b8a6',
        ];
        const bgColors     = labels.map((_, i) => PALETTE[i % PALETTE.length] + 'cc');
        const borderColors = labels.map((_, i) => PALETTE[i % PALETTE.length]);

        const cfg = {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Commits',
                    data: counts,
                    backgroundColor: bgColors,
                    borderColor:     borderColors,
                    borderWidth:     2,
                    borderRadius:    6,
                    borderSkipped:   false,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: getThemeColors().tooltipBg,
                        titleColor:      getThemeColors().tooltipFg,
                        bodyColor:       getThemeColors().tooltipFg,
                        borderColor:     '#6366f1',
                        borderWidth:     1,
                        padding:         10,
                        callbacks: {
                            label: (ctx) => ` ${ctx.parsed.y} commits`,
                        },
                    },
                },
                scales: {
                    x: {
                        grid:  { color: getThemeColors().gridColor },
                        ticks: { color: getThemeColors().labelColor, font: { size: 12 } },
                    },
                    y: {
                        beginAtZero: true,
                        grid:  { color: getThemeColors().gridColor },
                        ticks: {
                            color: getThemeColors().labelColor,
                            font:  { size: 12 },
                            stepSize: 1,
                            callback: (v) => Number.isInteger(v) ? v : null,
                        },
                    },
                },
            },
        };

        const chart = new Chart(chartCanvas, cfg);

        // Re-style chart when theme changes
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const tc = getThemeColors();
                chart.options.plugins.tooltip.backgroundColor = tc.tooltipBg;
                chart.options.plugins.tooltip.titleColor      = tc.tooltipFg;
                chart.options.plugins.tooltip.bodyColor       = tc.tooltipFg;
                chart.options.scales.x.grid.color   = tc.gridColor;
                chart.options.scales.x.ticks.color  = tc.labelColor;
                chart.options.scales.y.grid.color   = tc.gridColor;
                chart.options.scales.y.ticks.color  = tc.labelColor;
                chart.update();
            });
        }
    }

    /* ----------------------------------------------------------
       6. SMOOTH SCROLL to results after form submit
    ---------------------------------------------------------- */
    const results = document.getElementById('results');
    if (results && window.__REPO_DATA__) {
        // Small delay to let layout settle
        setTimeout(() => {
            results.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

})();

