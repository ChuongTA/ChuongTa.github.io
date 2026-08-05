/**
 * code-copy.js
 *
 * Injects a "Copy" button into the top-right area of every fenced code block
 * rendered by Jekyll + Rouge (Minimal Mistakes theme).
 *
 * HTML structure produced by Rouge:
 *   <div class="highlighter-rouge language-*">   ← container (position:relative, ::before = </> icon)
 *     <div class="highlight">
 *       <pre class="highlight"><code>…</code></pre>
 *     </div>
 *   </div>
 *
 * The ::before pseudo-element already sits at top:0 / right:0, so we place
 * the copy button just to the LEFT of it (right: 2.2em).
 */
(function () {
  "use strict";

  var LABEL_COPY    = "Copy";
  var LABEL_COPIED  = "Copied!";
  var RESET_MS      = 2000;

  function copyText(text, btn) {
    function onOk() {
      btn.textContent = LABEL_COPIED;
      btn.classList.add("is-copied");
      setTimeout(function () {
        btn.textContent = LABEL_COPY;
        btn.classList.remove("is-copied");
      }, RESET_MS);
    }

    function onErr(e) {
      console.warn("[code-copy] clipboard write failed:", e);
    }

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(onOk, onErr);
    } else {
      // execCommand fallback (HTTP or older browsers)
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.cssText = "position:fixed;top:0;left:0;opacity:0;pointer-events:none";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try { document.execCommand("copy"); onOk(); }
      catch (e) { onErr(e); }
      document.body.removeChild(ta);
    }
  }

  function injectButtons() {
    // Rouge wraps code in div.highlighter-rouge; figure.highlight covers
    // Jekyll's {% highlight %} liquid tag blocks.
    var containers = document.querySelectorAll(
      "div.highlighter-rouge:not(.code-copy-done), figure.highlight:not(.code-copy-done)"
    );

    containers.forEach(function (container) {
      container.classList.add("code-copy-done");

      var code = container.querySelector("code");
      if (!code) return;

      var btn = document.createElement("button");
      btn.className   = "code-copy-btn";
      btn.textContent = LABEL_COPY;
      btn.setAttribute("aria-label", "Copy code to clipboard");
      btn.setAttribute("type", "button");

      btn.addEventListener("click", function () {
        copyText(code.innerText || code.textContent, btn);
      });

      // The container already has position:relative from _syntax.scss.
      container.appendChild(btn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectButtons);
  } else {
    injectButtons();
  }
})();
