/* ONUA — shared interactions. All content lives in each HTML file; this file only adds behaviour. */
(function () {
  "use strict";
  document.documentElement.classList.add("js");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ---------- mobile navigation ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var menu = document.getElementById("site-menu");
  if (toggle && menu) {
    var setMenu = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.textContent = open ? "Close" : "Menu";
      menu.classList.toggle("is-open", open);
    };
    toggle.addEventListener("click", function () { setMenu(toggle.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("is-open")) { setMenu(false); toggle.focus(); }
    });
  }

  /* ---------- status and category filters (portfolio, events) ---------- */
  $$("[data-filter-group]").forEach(function (group) {
    var target = document.getElementById(group.getAttribute("data-filter-group"));
    if (!target) return;
    var items = $$("[data-tags]", target);
    var buttons = $$("[data-filter]", group);
    var status = document.getElementById(group.getAttribute("data-status"));
    var empty = document.getElementById(group.getAttribute("data-empty"));
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var f = btn.getAttribute("data-filter");
        var shown = 0;
        buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
        items.forEach(function (it) {
          var match = f === "all" || it.getAttribute("data-tags").split(" ").indexOf(f) > -1;
          it.hidden = !match;
          if (match) shown++;
        });
        if (empty) empty.hidden = shown !== 0;
        if (status) status.textContent = (btn.getAttribute("data-label") || btn.firstChild.textContent.trim()) + " · " + shown;
      });
    });
  });

  /* ---------- portfolio: one detail view per project (#project-name) ---------- */
  var index = document.querySelector(".works-index");
  var details = $$(".detail");
  if (index && details.length) {
    var route = function (first) {
      var id = decodeURIComponent(window.location.hash.replace("#", ""));
      var target = id ? document.getElementById(id) : null;
      var isDetail = target && target.classList.contains("detail");
      details.forEach(function (d) { d.classList.toggle("is-active", d === target); });
      index.classList.toggle("is-hidden", !!isDetail);
      if (isDetail) {
        document.title = target.getAttribute("data-title") + " · onua";
        window.scrollTo({ top: 0, behavior: "auto" });
        var h = target.querySelector("h1");
        if (h && !first) h.focus({ preventScroll: true });
      } else {
        document.title = "Portfolio · onua";
        var from = sessionStore("onua-last");
        if (from && !first) {
          var card = document.querySelector('.work[href="#' + from + '"]');
          if (card) { card.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" }); card.focus({ preventScroll: true }); }
        }
      }
      if (isDetail) sessionStore("onua-last", id);
    };
    function sessionStore(key, val) {
      try {
        if (val === undefined) return window.sessionStorage.getItem(key);
        window.sessionStorage.setItem(key, val);
      } catch (e) { return null; }
    }
    window.addEventListener("hashchange", function () { route(false); });
    route(true);
  }

  /* ---------- contact: enquiry type, prepare message (no server yet) ---------- */
  var form = document.getElementById("contact-form");
  if (form) {
    var hint = document.getElementById("type-hint");
    var hints = {
      story: "Who is behind the work, what they make, and why. You’re welcome to introduce someone else.",
      collab: "Tell us what you make and how you’d like to work with us.",
      partner: "Tell us about your organisation or space, and what you’d like to do together."
    };
    var setHint = function () {
      var c = form.querySelector("input[name='type']:checked");
      if (c && hint) hint.textContent = hints[c.value] || "";
    };
    $$("input[name='type']", form).forEach(function (r) { r.addEventListener("change", setHint); });
    var preset = function () {
      var m = form.querySelector("input[name='type'][value='" + window.location.hash.replace("#", "") + "']");
      if (m) { m.checked = true; setHint(); }
    };
    preset();
    window.addEventListener("hashchange", preset);

    var out = document.getElementById("prepared");
    var outText = document.getElementById("prepared-text");
    var copy = document.getElementById("copy-prepared");
    var copyStatus = document.getElementById("copy-status");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var firstBad = null;
      $$("input:not([type='radio']), textarea", form).forEach(function (f) {
        var err = document.getElementById(f.id + "-error");
        if (!err) return;
        if (f.checkValidity()) { err.hidden = true; f.removeAttribute("aria-invalid"); return; }
        err.hidden = false;
        err.textContent = f.type === "checkbox" ? "Please tick this box once you’ve read the notice." :
          f.validity.valueMissing ? "Please fill this in." :
          f.type === "email" ? "Please enter an email address like name@example.com." :
          f.type === "url" ? "Please enter a full link starting with https://" : "Please check this field.";
        f.setAttribute("aria-invalid", "true");
        if (!firstBad) firstBad = f;
      });
      if (firstBad) { firstBad.focus(); return; }
      var v = function (id) { var el = document.getElementById(id); return el ? el.value.trim() : ""; };
      var type = form.querySelector("input[name='type']:checked");
      outText.textContent =
        "Type: " + (type ? type.closest("label").querySelector(".t").textContent.trim() : "") + "\n" +
        "Name: " + v("name") + "\n" +
        "Email: " + v("email") + "\n" +
        "Field of work: " + v("field") + "\n" +
        "Reference link: " + (v("link") || "—") + "\n\n" +
        "Introduction:\n" + v("intro") + "\n\n" +
        "Help needed:\n" + v("help");
      out.hidden = false;
      if (copyStatus) copyStatus.textContent = "";
      out.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      var h = out.querySelector("h2");
      if (h) h.focus({ preventScroll: true });
    });

    if (copy) copy.addEventListener("click", function () {
      var fallback = function () {
        var range = document.createRange(); range.selectNodeContents(outText);
        var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
        copyStatus.textContent = "Text selected. Press Ctrl+C (or ⌘C) to copy it.";
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(outText.textContent).then(function () {
          copyStatus.textContent = "Copied. Keep it until our inbox opens.";
        }, fallback);
      } else { fallback(); }
    });
  }
})();
