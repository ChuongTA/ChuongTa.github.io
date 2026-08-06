/* ==========================================================================
   Various functions that we want to use within the template
   ========================================================================== */

// Determine the expected state of the theme toggle, which can be "dark", "light", or
// "system". Default is "system".
let determineThemeSetting = () => {
  let themeSetting = localStorage.getItem("theme");
  return (themeSetting != "dark" && themeSetting != "light" && themeSetting != "system") ? "system" : themeSetting;
};

// Determine the computed theme, which can be "dark" or "light". If the theme setting is
// "system", the computed theme is determined based on the user's system preference.
let determineComputedTheme = () => {
  let themeSetting = determineThemeSetting();
  if (themeSetting != "system") {
    return themeSetting;
  }
  return (userPref && userPref("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
};

// detect OS/browser preference
const browserPref = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

// Set the theme on page load or when explicitly called
let setTheme = (theme) => {
  const use_theme =
    theme ||
    localStorage.getItem("theme") ||
    $("html").attr("data-theme") ||
    browserPref;

  if (use_theme === "dark") {
    $("html").attr("data-theme", "dark");
    $("#theme-icon").removeClass("fa-sun").addClass("fa-moon");
  } else if (use_theme === "light") {
    $("html").removeAttr("data-theme");
    $("#theme-icon").removeClass("fa-moon").addClass("fa-sun");
  }
};

// Toggle the theme manually
var toggleTheme = () => {
  const current_theme = $("html").attr("data-theme");
  const new_theme = current_theme === "dark" ? "light" : "dark";
  localStorage.setItem("theme", new_theme);
  setTheme(new_theme);
};

/* ==========================================================================
   Plotly integration script so that Markdown codeblocks will be rendered
   ========================================================================== */

// Read the Plotly data from the code block, hide it, and render the chart as new node. This allows for the 
// JSON data to be retrieve when the theme is switched. The listener should only be added if the data is 
// actually present on the page.
import { plotlyDarkLayout, plotlyLightLayout } from './theme.js';
let plotlyElements = document.querySelectorAll("pre>code.language-plotly");
if (plotlyElements.length > 0) {
  document.addEventListener("readystatechange", () => {
    if (document.readyState === "complete") {
      plotlyElements.forEach((elem) => {
        // Parse the Plotly JSON data and hide it
        var jsonData = JSON.parse(elem.textContent);
        elem.parentElement.classList.add("hidden");

        // Add the Plotly node
        let chartElement = document.createElement("div");
        elem.parentElement.after(chartElement);

        // Set the theme for the plot and render it
        const theme = (determineComputedTheme() === "dark") ? plotlyDarkLayout : plotlyLightLayout;
        if (jsonData.layout) {
          jsonData.layout.template = (jsonData.layout.template) ? { ...theme, ...jsonData.layout.template } : theme;
        } else {
          jsonData.layout = { template: theme };
        }
        Plotly.react(chartElement, jsonData.data, jsonData.layout);
      });
    }
  });
}

/* ==========================================================================
   Actions that should occur when the page has been fully loaded
   ========================================================================== */

$(document).ready(function () {
  // SCSS SETTINGS - These should be the same as the settings in the relevant files 
  const scssLarge = 925;          // pixels, from /_sass/_themes.scss
  const scssMastheadHeight = 70;  // pixels, from the current theme (e.g., /_sass/theme/_default.scss)

  // If the user hasn't chosen a theme, follow the OS preference
  setTheme();
  window.matchMedia('(prefers-color-scheme: dark)')
        .addEventListener("change", (e) => {
          if (!localStorage.getItem("theme")) {
            setTheme(e.matches ? "dark" : "light");
          }
        });

  // Enable the theme toggle
  $('#theme-toggle').on('click', toggleTheme);

  // Enable the sticky footer
  var bumpIt = function () {
    $("body").css("margin-bottom", $(".page__footer").outerHeight(true));
  }
  $(window).resize(function () {
    didResize = true;
  });
  setInterval(function () {
    if (didResize) {
      didResize = false;
      bumpIt();
    }}, 250);
  var didResize = false;
  bumpIt();

  // FitVids init
  fitvids();

  // Follow menu drop down (direct child only — the Email button also lives
  // inside .author__urls-wrapper, nested under .author__urls, and must not
  // trigger this "Follow" toggle or it fades the whole icon list away)
  $(".author__urls-wrapper > button").on("click", function () {
    $(".author__urls").fadeToggle("fast", function () { });
    $(".author__urls-wrapper > button").toggleClass("open");
  });

  // Restore the follow menu if toggled on a window resize
  jQuery(window).on('resize', function () {
    if ($('.author__urls.social-icons').css('display') == 'none' && $(window).width() >= scssLarge) {
      $(".author__urls").css('display', 'block')
    }
  });

  // Init smooth scroll, this needs to be slightly more than then fixed masthead height
  $("a").smoothScroll({
    offset: -scssMastheadHeight,
    preventDefault: false,
  });

  // --- Client-side Search ---
  let searchData = null;
  const searchModal = $('#search-modal');
  const searchInput = $('#search-input');
  const searchResults = $('#search-results');

  // Toggle search modal
  $('#search-toggle').on('click', function(e) {
    e.preventDefault();
    searchModal.addClass('open');
    setTimeout(() => searchInput.focus(), 100);
    // Fetch search index if not already loaded
    if (!searchData) {
      const siteUrl = window.location.pathname.startsWith('/ChuongTa.github.io') ? '/ChuongTa.github.io' : '';
      fetch(siteUrl + '/search.json')
        .then(res => res.json())
        .then(data => {
          searchData = data;
        })
        .catch(err => console.error('Error loading search index:', err));
    }
  });

  $('#search-close, .search-modal__overlay').on('click', function() {
    searchModal.removeClass('open');
  });

  // Handle escape key to close modal
  $(document).on('keydown', function(e) {
    if (e.key === 'Escape' && searchModal.hasClass('open')) {
      searchModal.removeClass('open');
    }
  });

  // Perform search matching
  searchInput.on('input', function() {
    const query = $(this).val().toLowerCase().trim();
    if (!query) {
      searchResults.html('<div class="search-results-placeholder">Type to search...</div>');
      return;
    }
    if (!searchData) {
      searchResults.html('<div class="search-results-placeholder">Loading search index...</div>');
      return;
    }

    const matches = searchData.filter(item => {
      return (item.title && item.title.toLowerCase().includes(query)) || 
             (item.excerpt && item.excerpt.toLowerCase().includes(query));
    });

    if (matches.length === 0) {
      searchResults.html('<div class="search-results-placeholder">No results found</div>');
      return;
    }

    const html = matches.map(item => `
      <a href="${item.url}" class="search-result-item">
        <h3>${item.title}</h3>
        <p>${item.excerpt || ''}</p>
      </a>
    `).join('');
    searchResults.html(html);
  });

  // --- Scroll-to-Top Button ---
  const scrollTopBtn = $('#scroll-top-btn');
  $(window).on('scroll', function() {
    if ($(window).scrollTop() > 300) {
      scrollTopBtn.addClass('show');
    } else {
      scrollTopBtn.removeClass('show');
    }
  });

  scrollTopBtn.on('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  // --- Email Popup & Letter-Carrier Animation ---
  const emailBtn      = document.getElementById('email-btn');
  const emailPopup    = document.getElementById('email-popup');
  const emailCopyBtn  = document.getElementById('email-copy-btn');
  const emailCopiedMsg = document.getElementById('email-copied-msg');
  const letterCarrier = document.getElementById('letter-carrier');

  function runCarrier() {
    if (!letterCarrier) return;
    letterCarrier.classList.remove('running');
    // Force reflow to restart animation
    void letterCarrier.offsetWidth;
    letterCarrier.classList.add('running');
    letterCarrier.addEventListener('animationend', function onEnd() {
      letterCarrier.classList.remove('running');
      letterCarrier.removeEventListener('animationend', onEnd);
    });
  }

  function closePopup() {
    if (emailPopup) emailPopup.hidden = true;
    if (emailCopiedMsg) {
      emailCopiedMsg.classList.remove('visible');
      emailCopiedMsg.textContent = '';
    }
  }

  if (emailBtn && emailPopup) {
    emailBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      const isHidden = emailPopup.hidden;
      emailPopup.hidden = !isHidden;
    });
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  function onCopySuccess() {
    if (emailCopiedMsg) {
      emailCopiedMsg.textContent = '✓ Copied!';
      emailCopiedMsg.classList.add('visible');
    }
    setTimeout(function() {
      closePopup();
      runCarrier();
    }, 900);
  }

  if (emailCopyBtn && emailPopup) {
    emailCopyBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      const address = emailPopup.querySelector('.email-popup__address');
      if (!address) return;
      const text = address.textContent.trim();

      // execCommand is synchronous and needs no permissions/secure-context
      // checks, so it's the more reliable path — try it first, and only
      // reach for the async Clipboard API if it fails.
      if (fallbackCopy(text)) {
        onCopySuccess();
      } else if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(onCopySuccess, function(err) {
          console.warn('[email-copy] clipboard write failed', err);
        });
      }
    });
  }

  // Click outside to close popup and send the carrier
  document.addEventListener('click', function(e) {
    if (emailPopup && !emailPopup.hidden) {
      if (!emailPopup.contains(e.target) && e.target !== emailBtn) {
        closePopup();
        runCarrier();
      }
    }
  });

});

