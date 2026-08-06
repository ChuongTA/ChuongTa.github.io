/**
 * toc-spy.js
 *
 * Builds a sticky "On this page" table-of-contents panel on the right
 * side of every post/page.  Active section is highlighted as you scroll
 * using IntersectionObserver (no scroll event polling).
 *
 * Only activates when:
 *   - The page has a .page__content element
 *   - That element contains at least 2 headings (h2 or h3)
 */
(function () {
  "use strict";

  /* ── Config ─────────────────────────────────────────────── */
  var HEADING_SELECTOR = ".page__content h2, .page__content h3";
  var MIN_HEADINGS     = 2;      // don't show TOC for very short pages
  var OFFSET_TOP       = 90;     // px — below the masthead

  /* ── Helpers ─────────────────────────────────────────────── */
  function slug(el) {
    // Re-use an existing id; otherwise derive one from the text
    if (el.id) return el.id;
    var id = el.textContent
      .trim()
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .replace(/\s+/g, "-");
    el.id = id;
    return id;
  }

  function buildTOC(headings) {
    /* ── Panel shell ──────────────────────────────────────── */
    var panel = document.createElement("nav");
    panel.id        = "toc-panel";
    panel.className = "toc-panel";
    panel.setAttribute("aria-label", "Table of contents");

    /* Header row */
    var header = document.createElement("div");
    header.className = "toc-panel__header";

    var title = document.createElement("span");
    title.className   = "toc-panel__title";
    title.textContent = "On this page";

    var closeBtn = document.createElement("button");
    closeBtn.className   = "toc-panel__close";
    closeBtn.textContent = "×";
    closeBtn.setAttribute("aria-label", "Close table of contents");
    closeBtn.setAttribute("type", "button");

    header.appendChild(title);
    header.appendChild(closeBtn);
    panel.appendChild(header);

    /* List */
    var list = document.createElement("ol");
    list.className = "toc-panel__list";

    var items = []; // { el: liElement, headingEl: h }

    headings.forEach(function (h) {
      var id   = slug(h);
      var li   = document.createElement("li");
      var link = document.createElement("a");

      li.className   = "toc-panel__item toc-panel__item--" + h.tagName.toLowerCase();
      link.href      = "#" + id;
      link.textContent = h.textContent.trim();
      link.className = "toc-panel__link";

      // Smooth scroll
      link.addEventListener("click", function (e) {
        e.preventDefault();
        var target = document.getElementById(id);
        if (target) {
          window.scrollTo({
            top: target.getBoundingClientRect().top + window.scrollY - OFFSET_TOP,
            behavior: "smooth"
          });
        }
      });

      li.appendChild(link);
      list.appendChild(li);
      items.push({ li: li, h: h });
    });

    panel.appendChild(list);

    /* ── Floating toggle button (shown when panel is hidden) ── */
    var toggle = document.createElement("button");
    toggle.id        = "toc-toggle";
    toggle.className = "toc-toggle";
    toggle.setAttribute("aria-label", "Open table of contents");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("type", "button");
    toggle.innerHTML = [
      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"',
      ' viewBox="0 0 24 24" fill="none" stroke="currentColor"',
      ' stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"',
      ' aria-hidden="true">',
      '<line x1="3" y1="6"  x2="21" y2="6"/>',
      '<line x1="3" y1="12" x2="21" y2="12"/>',
      '<line x1="3" y1="18" x2="15" y2="18"/>',
      '</svg>'
    ].join("");

    /* ── Visibility logic ─────────────────────────────────── */
    function hidePanel() {
      panel.classList.add("toc-panel--hidden");
      toggle.setAttribute("aria-expanded", "false");
    }
    function showPanel() {
      panel.classList.remove("toc-panel--hidden");
      toggle.setAttribute("aria-expanded", "true");
    }

    closeBtn.addEventListener("click", hidePanel);
    toggle.addEventListener("click", function () {
      if (panel.classList.contains("toc-panel--hidden")) {
        showPanel();
      } else {
        hidePanel();
      }
    });

    /* ── Inject ───────────────────────────────────────────── */
    document.body.appendChild(panel);
    document.body.appendChild(toggle);

    /* ── Scroll spy via IntersectionObserver ──────────────── */
    var activeItem = null;

    function setActive(li) {
      if (activeItem) activeItem.classList.remove("toc-panel__item--active");
      activeItem = li;
      if (li) {
        li.classList.add("toc-panel__item--active");
        // Scroll the TOC list so the active item is visible
        var listTop  = list.getBoundingClientRect().top;
        var itemTop  = li.getBoundingClientRect().top;
        var listH    = list.clientHeight;
        var itemH    = li.clientHeight;
        var relative = itemTop - listTop;
        if (relative < 0 || relative + itemH > listH) {
          list.scrollTop += relative - listH / 2 + itemH / 2;
        }
      }
    }

    // Map heading element → list item for O(1) lookup
    var headingToItem = new Map();
    items.forEach(function (obj) { headingToItem.set(obj.h, obj.li); });

    // Use a rootMargin that fires slightly before the heading reaches the top
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          setActive(headingToItem.get(entry.target));
        }
      });
    }, {
      rootMargin: "-" + OFFSET_TOP + "px 0px -60% 0px",
      threshold:  0
    });

    headings.forEach(function (h) { observer.observe(h); });
  }

  /* ── Boot ────────────────────────────────────────────────── */
  function init() {
    if (document.body.classList.contains('homepage-layout')) return;
    var headings = Array.from(document.querySelectorAll(HEADING_SELECTOR));
    if (headings.length < MIN_HEADINGS) return;   // not worth showing
    buildTOC(headings);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
