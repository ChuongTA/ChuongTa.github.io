/**
 * code-copy.js
 *
 * Adds a copy button (clipboard icon) to every fenced code block.
 * Default state : clipboard SVG icon
 * After click   : shows "Copied!" text for 2 s, then reverts to icon
 */
(function () {
  "use strict";

  var RESET_MS = 2000;

  // Two-rectangle clipboard SVG (Feather Icons style)
  var ICON_SVG = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"',
    ' viewBox="0 0 24 24" fill="none" stroke="currentColor"',
    ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"',
    ' aria-hidden="true">',
    '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>',
    '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    '</svg>'
  ].join("");

  function setIcon(btn) {
    btn.innerHTML = ICON_SVG;
    btn.classList.remove("is-copied");
  }

  function setCopied(btn) {
    btn.textContent = "Copied!";
    btn.classList.add("is-copied");
    setTimeout(function () { setIcon(btn); }, RESET_MS);
  }

  function copyText(text, btn) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(
        function () { setCopied(btn); },
        function (e) { console.warn("[code-copy]", e); }
      );
    } else {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.cssText = "position:fixed;top:0;left:0;opacity:0;pointer-events:none";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try { document.execCommand("copy"); setCopied(btn); }
      catch (e) { console.warn("[code-copy]", e); }
      document.body.removeChild(ta);
    }
  }

  function injectButtons() {
    document.querySelectorAll(
      "div.highlighter-rouge:not(.code-copy-done), figure.highlight:not(.code-copy-done)"
    ).forEach(function (container) {
      container.classList.add("code-copy-done");

      var code = container.querySelector("code");
      if (!code) return;

      var btn = document.createElement("button");
      btn.className = "code-copy-btn";
      btn.setAttribute("aria-label", "Copy code to clipboard");
      btn.setAttribute("type", "button");
      setIcon(btn);   // start with the clipboard icon

      btn.addEventListener("click", function () {
        copyText(code.innerText || code.textContent, btn);
      });

      container.appendChild(btn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectButtons);
  } else {
    injectButtons();
  }
})();
