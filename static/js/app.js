/* ==========================================================================
   hesam.ir — progressive enhancement only.

   The server already sent a finished page. Nothing in this file is required
   for the site to be read, navigated or submitted: turn JavaScript off and
   every link, form and page still works. What this adds is the difference
   between "it works" and "it feels considered".

   No framework, no build step, no dependency. One file, one function per
   concern, all started from boot() at the bottom.
   ========================================================================== */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var isPersian = (root.getAttribute("lang") || "").indexOf("fa") === 0;
  var STORE_THEME = "naderirad-theme";
  // The two values of --bg in site.css. The <meta name="theme-color"> tags in
  // base.html carry the same pair; if the tokens change, these change too.
  var THEME_COLOR = { light: "#f4f5f7", dark: "#12141b" };

  /* ── small helpers ─────────────────────────────────────────────────── */
  function $(sel, scope) { return (scope || document).querySelector(sel); }
  function $$(sel, scope) { return Array.prototype.slice.call((scope || document).querySelectorAll(sel)); }

  // The canvas layers draw in the --x-rgb tokens, so they read them from CSS
  // and read them again whenever the theme changes — by the switch in the
  // header (data-theme) or by the device (prefers-color-scheme).
  var HUES = ["mint", "sky", "lilac", "peach"];
  function readPalette() {
    var cs = getComputedStyle(root), pal = { mono: cs.getPropertyValue("--mono").trim() || "monospace" };
    HUES.forEach(function (hue) { pal[hue] = cs.getPropertyValue("--" + hue + "-rgb").trim() || "128,128,128"; });
    return pal;
  }
  function onThemeChange(fn) {
    new MutationObserver(fn).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
    var scheme = window.matchMedia("(prefers-color-scheme: dark)");
    if (scheme.addEventListener) scheme.addEventListener("change", fn);
    else if (scheme.addListener) scheme.addListener(fn);
  }

  function icon(name, cls) {
    var ns = "http://www.w3.org/2000/svg";
    var svg = document.createElementNS(ns, "svg");
    svg.setAttribute("aria-hidden", "true");
    if (cls) svg.setAttribute("class", cls);
    var use = document.createElementNS(ns, "use");
    use.setAttribute("href", "#i-" + name);
    svg.appendChild(use);
    return svg;
  }

  function digits(n) {
    var s = String(n);
    return isPersian ? s.replace(/\d/g, function (d) { return "۰۱۲۳۴۵۶۷۸۹"[d]; }) : s;
  }

  var toastTimer = null;
  function toast(text, iconName) {
    var old = $(".toast");
    if (old) old.remove();
    var el = document.createElement("div");
    el.className = "toast";
    el.setAttribute("role", "status");
    var ico = document.createElement("span");
    ico.className = "toast-ico";
    ico.appendChild(icon(iconName || "check"));
    var label = document.createElement("span");
    label.textContent = text;
    el.appendChild(ico);
    el.appendChild(label);
    document.body.appendChild(el);
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      el.classList.add("is-leaving");
      setTimeout(function () { el.remove(); }, 260);
    }, 2200);
  }

  /* ══ theme ═════════════════════════════════════════════════════════════
     Three states, not two: system / light / dark. "system" removes the
     attribute so the media query in the stylesheet decides. The same key is
     read by the pre-paint snippet in the <head> of base.html — if you rename
     it here, rename it there, or the page flashes the wrong theme for a frame.
     ══════════════════════════════════════════════════════════════════════ */
  function readTheme() {
    try { return localStorage.getItem(STORE_THEME) || "system"; } catch (e) { return "system"; }
  }
  function applyTheme(value) {
    if (value === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", value);
    try { localStorage.setItem(STORE_THEME, value); } catch (e) { /* private mode */ }
    // An explicit choice paints the browser chrome that colour on every
    // device; "system" hands each meta tag back to its own media query.
    $$('meta[name="theme-color"]').forEach(function (meta) {
      var media = meta.getAttribute("media") || "";
      var own = media.indexOf("dark") > -1 ? "dark" : "light";
      meta.setAttribute("content", THEME_COLOR[value === "system" ? own : value]);
    });
  }
  function nextTheme() {
    var order = ["system", "light", "dark"];
    return order[(order.indexOf(readTheme()) + 1) % order.length];
  }
  function cycleTheme() {
    var btn = $("[data-theme-cycle]");
    var next = nextTheme();
    applyTheme(next);
    if (btn) {
      btn.classList.remove("is-turning");
      void btn.offsetWidth;
      btn.classList.add("is-turning");
      toast(btn.dataset["label" + next.charAt(0).toUpperCase() + next.slice(1)] || next, next === "dark" ? "moon" : next === "light" ? "sun" : "monitor");
    }
  }
  function initTheme() {
    applyTheme(readTheme());
    var btn = $("[data-theme-cycle]");
    if (btn) btn.addEventListener("click", cycleTheme);
  }

  /* ══ header: frosting, reading progress, back-to-top, mobile nav ═══════ */
  function initHeader() {
    var hdr = $("[data-hdr]");
    if (!hdr) return;
    var bar = $("[data-progress]");
    var toTop = $("[data-to-top-float]");
    var ring = toTop && $(".bar", toTop);
    var RING = 138.2; // 2πr for r = 22 in the ring's viewBox
    var ticking = false;

    if (toTop) { toTop.hidden = false; toTop.tabIndex = -1; }

    function update() {
      ticking = false;
      var y = window.scrollY;
      var max = root.scrollHeight - window.innerHeight;
      var p = max > 0 ? Math.min(1, y / max) : 0;
      hdr.classList.toggle("is-stuck", y > 8);
      if (bar) bar.style.transform = "scaleX(" + p.toFixed(4) + ")";
      if (toTop) {
        var on = y > 700;
        if (on !== toTop.classList.contains("is-on")) {
          toTop.classList.toggle("is-on", on);
          toTop.tabIndex = on ? 0 : -1;
          toTop.setAttribute("aria-hidden", String(!on));
        }
        if (ring) ring.style.strokeDashoffset = String(RING * (1 - p));
      }
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener("resize", update);
    update();

    $$("[data-to-top], [data-to-top-float]").forEach(function (b) {
      b.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      });
    });

    var burger = $("[data-burger]");
    var mnav = $("[data-mnav]");
    if (burger && mnav) {
      var setOpen = function (open) {
        mnav.toggleAttribute("hidden", !open);
        burger.setAttribute("aria-expanded", String(open));
        hdr.classList.toggle("is-open", open);
      };
      burger.addEventListener("click", function (e) {
        e.stopPropagation();
        setOpen(mnav.hasAttribute("hidden"));
      });
      document.addEventListener("click", function (e) {
        if (!mnav.hasAttribute("hidden") && !hdr.contains(e.target)) setOpen(false);
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && !mnav.hasAttribute("hidden")) { setOpen(false); burger.focus(); }
      });
      window.addEventListener("resize", function () {
        if (window.innerWidth > 960 && !mnav.hasAttribute("hidden")) setOpen(false);
      });
    }
  }

  /* ══ nav indicator ═════════════════════════════════════════════════════
     One soft pill that slides to whichever link the pointer is on and back
     to the current page when it leaves. Without this, .is-active paints its
     own background and nothing moves.
     ══════════════════════════════════════════════════════════════════════ */
  function initNavIndicator() {
    var nav = $("[data-nav]");
    var ind = nav && $(".nav-ind", nav);
    if (!ind) return;
    var active = $("a.is-active", nav);
    nav.classList.add("has-ind");

    function moveTo(a) {
      if (!a || !a.offsetWidth) { ind.style.opacity = "0"; return; }
      ind.style.opacity = "1";
      ind.style.width = a.offsetWidth + "px";
      ind.style.transform = "translateX(" + a.offsetLeft + "px)";
    }
    ind.classList.add("no-anim");
    moveTo(active);
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () { ind.classList.remove("no-anim"); });
    });
    $$("a", nav).forEach(function (a) {
      a.addEventListener("pointerenter", function () { moveTo(a); });
      a.addEventListener("focus", function () { moveTo(a); });
    });
    nav.addEventListener("pointerleave", function () { moveTo(active); });
    nav.addEventListener("focusout", function (e) { if (!nav.contains(e.relatedTarget)) moveTo(active); });
    window.addEventListener("resize", function () { moveTo(active); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { moveTo(active); });
  }

  /* ══ popovers (language menu) ══════════════════════════════════════════ */
  function initPopovers() {
    var open = null;
    function close(returnFocus) {
      if (!open) return;
      open.menu.setAttribute("hidden", "");
      open.btn.setAttribute("aria-expanded", "false");
      if (returnFocus) open.btn.focus();
      open = null;
    }
    $$("[data-popover]").forEach(function (wrap) {
      var btn = $("[data-popover-btn]", wrap);
      var menu = $("[data-popover-menu]", wrap);
      if (!btn || !menu) return;
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        var wasOpen = open && open.menu === menu;
        close();
        if (!wasOpen) {
          menu.removeAttribute("hidden");
          btn.setAttribute("aria-expanded", "true");
          open = { btn: btn, menu: menu };
          var current = $('[aria-current="true"]', menu) || $("a", menu);
          if (current && e.detail === 0) current.focus(); // keyboard-opened only
        }
      });
      menu.addEventListener("keydown", function (e) {
        if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
        e.preventDefault();
        var items = $$("a", menu);
        var i = items.indexOf(document.activeElement);
        items[(i + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length].focus();
      });
    });
    document.addEventListener("click", function () { close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(true); });
  }

  /* ══ tooltips ══════════════════════════════════════════════════════════
     Any element with data-tip="…" gets one. A single floating element is
     positioned against the viewport, flips below when there is no room
     above and never runs off either edge. Mouse hover and keyboard focus
     only — on touch, the aria-label the element already carries is enough.
     ══════════════════════════════════════════════════════════════════════ */
  var tipApi = { show: function () {}, hide: function () {}, current: null };
  function initTips() {
    var tip = document.createElement("div");
    tip.className = "tip";
    tip.id = "site-tip";
    tip.setAttribute("role", "tooltip");
    document.body.appendChild(tip);
    var timer = null;

    function place(el) {
      var r = el.getBoundingClientRect();
      var tw = tip.offsetWidth, th = tip.offsetHeight, gap = 10;
      var top = r.top - th - gap, where = "top";
      if (top < 8) { top = r.bottom + gap; where = "bottom"; }
      var left = r.left + r.width / 2 - tw / 2;
      left = Math.max(8, Math.min(left, window.innerWidth - tw - 8));
      tip.dataset.place = where;
      tip.style.left = left + "px";
      tip.style.top = top + "px";
      tip.style.setProperty("--ax", Math.max(12, Math.min(tw - 12, r.left + r.width / 2 - left)) + "px");
    }
    function show(el) {
      var text = el.getAttribute("data-tip");
      if (!text) return;
      tipApi.current = el;
      tip.textContent = text;
      tip.classList.remove("is-on");
      place(el);
      if (!el.hasAttribute("aria-label")) el.setAttribute("aria-describedby", tip.id);
      window.requestAnimationFrame(function () { tip.classList.add("is-on"); });
    }
    function hide() {
      clearTimeout(timer);
      if (tipApi.current) tipApi.current.removeAttribute("aria-describedby");
      tipApi.current = null;
      tip.classList.remove("is-on");
    }
    tipApi.show = show;
    tipApi.hide = hide;

    document.addEventListener("pointerover", function (e) {
      if (e.pointerType && e.pointerType !== "mouse") return;
      var el = e.target.closest && e.target.closest("[data-tip]");
      if (!el || el === tipApi.current) return;
      clearTimeout(timer);
      timer = setTimeout(function () { show(el); }, tipApi.current ? 0 : 160);
    });
    document.addEventListener("pointerout", function (e) {
      var el = e.target.closest && e.target.closest("[data-tip]");
      if (!el || (e.relatedTarget && el.contains(e.relatedTarget))) return;
      hide();
    });
    document.addEventListener("focusin", function (e) {
      var el = e.target.closest && e.target.closest("[data-tip]");
      if (el && el.matches(":focus-visible")) show(el);
    });
    document.addEventListener("focusout", hide);
    document.addEventListener("pointerdown", hide);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") hide(); });
    window.addEventListener("scroll", hide, { passive: true });
  }

  /* ══ reveal on scroll ══════════════════════════════════════════════════
     The resting state in CSS is visible; the hidden state only exists while
     .js is on and motion is allowed. Without IntersectionObserver every
     .reveal is shown immediately, which is the correct failure. Items that
     arrive together are staggered by --d, which only the arrival animation
     reads — hover transitions stay instant.
     ══════════════════════════════════════════════════════════════════════ */
  function initReveal() {
    var items = $$(".reveal");
    if (!items.length) return;
    if (reduceMotion || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      var n = 0;
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.style.setProperty("--d", Math.min(n++, 6) * 80 + "ms");
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ══ pointer effects: spotlight and tilt ═══════════════════════════════
     Fine pointers only, and never under reduced motion. Both write CSS
     custom properties; the stylesheet decides what they look like.
     ══════════════════════════════════════════════════════════════════════ */
  function initPointer() {
    if (!finePointer || reduceMotion) return;
    document.addEventListener("pointermove", function (e) {
      var el = e.target.closest && e.target.closest("[data-spot]");
      if (!el) return;
      var r = el.getBoundingClientRect();
      el.style.setProperty("--mx", (e.clientX - r.left) + "px");
      el.style.setProperty("--my", (e.clientY - r.top) + "px");
    }, { passive: true });

    /* The pinned backdrop photo lies under the content and takes no pointer
       events, so it cannot be hovered: its flashlight follows the pointer
       through the whole page instead, once per frame. */
    var lit = $(".photo-stand.photo-lit"), px = 0, py = 0, queued = false;
    if (lit) {
      var aim = function () {
        queued = false;
        var r = lit.getBoundingClientRect();
        var inside = px >= r.left && px <= r.right && py >= r.top && py <= r.bottom;
        lit.classList.toggle("is-lit", inside);
        if (inside) {
          lit.style.setProperty("--mx", (px - r.left) + "px");
          lit.style.setProperty("--my", (py - r.top) + "px");
        }
      };
      document.addEventListener("pointermove", function (e) {
        px = e.clientX; py = e.clientY;
        if (!queued) { queued = true; requestAnimationFrame(aim); }
      }, { passive: true });
      document.documentElement.addEventListener("pointerleave", function () { lit.classList.remove("is-lit"); });
    }

    $$("[data-tilt]").forEach(function (el) {
      var max = parseFloat(el.dataset.tilt) || 6;
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        el.classList.add("is-tilting");
        el.style.setProperty("--ry", (x * max * 2).toFixed(2) + "deg");
        el.style.setProperty("--rx", (-y * max * 2).toFixed(2) + "deg");
        el.style.setProperty("--gx", ((x + 0.5) * 100).toFixed(1) + "%");
        el.style.setProperty("--gy", ((y + 0.5) * 100).toFixed(1) + "%");
      });
      el.addEventListener("pointerleave", function () {
        el.classList.remove("is-tilting");
        el.style.setProperty("--rx", "0deg");
        el.style.setProperty("--ry", "0deg");
      });
    });
  }

  /* ══ tag filter ════════════════════════════════════════════════════════
     Client-side because the whole list is already on the page. The query
     string is kept in step so a filtered view is still a shareable URL, and
     the server honours ?tag= on a cold load.
     ══════════════════════════════════════════════════════════════════════ */
  function initFilter() {
    var bar = $("[data-filter-bar]");
    var listing = $("[data-filter-list]");
    if (!bar || !listing) return;
    var empty = $("[data-filter-empty]");
    var items = $$("[data-tags]", listing);

    function apply(tag, push) {
      var shown = 0;
      items.forEach(function (el) {
        var match = !tag || (" " + el.dataset.tags + " ").indexOf(" " + tag + " ") > -1;
        if (match) {
          shown++;
          if (el.hidden) {
            el.hidden = false;
            if (push && !reduceMotion) {
              el.classList.remove("is-pop");
              void el.offsetWidth;
              el.classList.add("is-pop");
            }
          }
        } else {
          el.hidden = true;
        }
      });
      if (empty) empty.hidden = shown !== 0;
      $$("[data-tag]", bar).forEach(function (b) {
        b.setAttribute("aria-pressed", String((b.dataset.tag || "") === tag));
      });
      if (push) {
        var url = new URL(window.location.href);
        if (tag) url.searchParams.set("tag", tag); else url.searchParams.delete("tag");
        history.replaceState(null, "", url);
      }
    }

    bar.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-tag]");
      if (!btn) return;
      apply(btn.dataset.tag || "", true);
    });

    apply(new URL(window.location.href).searchParams.get("tag") || "", false);
  }

  /* ══ copy to clipboard ═════════════════════════════════════════════════ */
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () { return legacyCopy(text); });
    }
    return legacyCopy(text);
  }
  function legacyCopy(text) {
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy") ? resolve() : reject(); } catch (err) { reject(err); }
      ta.remove();
    });
  }
  function flashDone(btn) {
    var use = $("use", btn);
    if (!use || btn.classList.contains("is-done")) return;
    var old = use.getAttribute("href");
    use.setAttribute("href", "#i-check");
    btn.classList.add("is-done");
    setTimeout(function () { use.setAttribute("href", old); btn.classList.remove("is-done"); }, 1600);
  }
  function initCopy() {
    document.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-copy]");
      if (!btn) return;
      e.preventDefault();
      copyText(btn.dataset.copy).then(function () {
        flashDone(btn);
        toast(btn.dataset.copiedLabel || "Copied");
      }, function () { /* nothing else to try */ });
    });
  }

  /* ══ share ═════════════════════════════════════════════════════════════ */
  function initShare() {
    document.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-share]");
      if (!btn) return;
      e.preventDefault();
      var payload = { title: document.title, url: btn.dataset.share || window.location.href };
      if (navigator.share) {
        navigator.share(payload).catch(function () { /* the reader dismissed it */ });
      } else {
        copyText(payload.url).then(function () { toast(btn.dataset.copiedLabel || "Copied", "share"); });
      }
    });
  }

  /* ══ contact form: character count and the sending state ═══════════════ */
  function initForms() {
    $$("[data-form]").forEach(function (form) {
      var area = $("[data-count]", form);
      var counter = $("[data-counter]", form);
      if (area && counter) {
        var max = parseInt(area.getAttribute("maxlength"), 10) || 0;
        var update = function () {
          var n = area.value.length;
          counter.textContent = digits(n) + " / " + digits(max);
          counter.classList.toggle("is-near", max && n > max * 0.9);
        };
        area.addEventListener("input", update);
        update();
      }
      // Email or phone, at least one. The server checks the same rule and is
      // the authority; this only saves the round trip and says it in place.
      var reach = $("[data-reach]", form);
      var reachErr = reach && $("[data-reach-err]", reach);
      var reachInputs = reach ? $$("input", reach) : [];
      var reachMet = function () {
        return reachInputs.some(function (i) { return i.value.trim() !== ""; });
      };
      reachInputs.forEach(function (i) {
        i.addEventListener("input", function () {
          if (!reach.classList.contains("is-invalid") || !reachMet()) return;
          reach.classList.remove("is-invalid");
          if (reachErr) reachErr.hidden = true;
        });
      });
      form.addEventListener("submit", function (e) {
        if (reach && !reachMet()) {
          e.preventDefault();
          reach.classList.add("is-invalid");
          if (reachErr) reachErr.hidden = false;
          reachInputs[0].focus();
          reach.scrollIntoView({ block: "center", behavior: reduceMotion ? "auto" : "smooth" });
          return;
        }
        var btn = $("[data-submit]", form);
        if (!btn) return;
        btn.classList.add("is-loading");
        btn.setAttribute("aria-busy", "true");
        var label = $(".btn-label", btn);
        if (label && btn.dataset.busyLabel) label.textContent = btn.dataset.busyLabel;
      });
    });
    // Coming back through the history cache must not leave a spinner behind.
    window.addEventListener("pageshow", function (e) {
      if (!e.persisted) return;
      $$("[data-submit].is-loading").forEach(function (b) { b.classList.remove("is-loading"); b.removeAttribute("aria-busy"); });
    });
  }

  /* ══ command palette ═══════════════════════════════════════════════════
     Ctrl/⌘+K, or "/". The index is rendered into the page as JSON by
     base.html, so it costs no request and knows about exactly the pages this
     reader can see. The language and theme shortcuts are read from the page
     itself, so they can never disagree with the header.
     ══════════════════════════════════════════════════════════════════════ */
  function initPalette() {
    var box = $("[data-cmdk]");
    if (!box) return;
    var input = $(".cmdk-input", box);
    var list = $(".cmdk-list", box);
    var data = [];
    try { data = JSON.parse($("#cmdk-data").textContent); } catch (e) { return; }

    var groupPages = box.dataset.groupPages || "Pages";
    var groupActions = box.dataset.groupActions || "Actions";
    $$(".lang-menu a").forEach(function (a) {
      if (a.getAttribute("aria-current") === "true") return;
      data.push({ t: a.textContent.replace(/\s+/g, " ").trim(), u: a.getAttribute("href"), k: groupActions, i: "globe" });
    });
    var themeBtn = $("[data-theme-cycle]");
    if (themeBtn) data.push({ t: themeBtn.getAttribute("aria-label"), k: groupActions, i: "sun", run: cycleTheme });

    var cursor = 0, results = [], opener = null;

    function highlight(text, q) {
      var frag = document.createDocumentFragment();
      var i = q ? text.toLowerCase().indexOf(q) : -1;
      if (i < 0) { frag.appendChild(document.createTextNode(text)); return frag; }
      frag.appendChild(document.createTextNode(text.slice(0, i)));
      var m = document.createElement("mark");
      m.textContent = text.slice(i, i + q.length);
      frag.appendChild(m);
      frag.appendChild(document.createTextNode(text.slice(i + q.length)));
      return frag;
    }

    function render(query) {
      var q = query.trim().toLowerCase();
      results = data.filter(function (item) {
        return !q || (item.t + " " + (item.k || "")).toLowerCase().indexOf(q) > -1;
      });
      cursor = 0;
      list.innerHTML = "";
      if (!results.length) {
        var none = document.createElement("div");
        none.className = "cmdk-empty";
        none.textContent = box.dataset.empty || "No results";
        list.appendChild(none);
        return;
      }
      var lastGroup = null;
      results.forEach(function (item, i) {
        var group = item.k || groupPages;
        if (group !== lastGroup) {
          var h = document.createElement("div");
          h.className = "cmdk-group";
          h.setAttribute("role", "presentation");
          h.textContent = group;
          list.appendChild(h);
          lastGroup = group;
        }
        var a = document.createElement(item.run ? "button" : "a");
        a.className = "cmdk-item" + (i === 0 ? " is-on" : "");
        a.setAttribute("role", "option");
        a.dataset.index = String(i);
        if (item.run) { a.type = "button"; a.style.width = "100%"; a.style.border = "0"; a.style.background = "none"; a.style.textAlign = "start"; }
        else a.href = item.u;
        var ci = document.createElement("span");
        ci.className = "ci";
        ci.appendChild(icon(item.i || "arrow"));
        var label = document.createElement("span");
        label.className = "ct";
        label.appendChild(highlight(item.t, q));
        a.appendChild(ci);
        a.appendChild(label);
        a.appendChild(icon("arrow", "go fwd"));
        a.addEventListener("pointermove", function () { setCursor(i); });
        if (item.run) a.addEventListener("click", function () { close(); item.run(); });
        list.appendChild(a);
      });
    }

    function nodes() { return $$(".cmdk-item", list); }
    function setCursor(i) {
      var all = nodes();
      if (!all.length) return;
      if (all[cursor]) all[cursor].classList.remove("is-on");
      cursor = (i + all.length) % all.length;
      all[cursor].classList.add("is-on");
      all[cursor].scrollIntoView({ block: "nearest" });
    }

    function open() {
      opener = document.activeElement;
      box.classList.remove("is-closing");
      box.removeAttribute("hidden");
      root.classList.add("is-locked");
      tipApi.hide();
      input.value = "";
      render("");
      input.focus();
    }
    function close() {
      if (box.hasAttribute("hidden")) return;
      root.classList.remove("is-locked");
      var done = function () { box.setAttribute("hidden", ""); box.classList.remove("is-closing"); };
      if (reduceMotion) done();
      else { box.classList.add("is-closing"); setTimeout(done, 160); }
      if (opener && opener.focus) opener.focus();
    }

    document.addEventListener("keydown", function (e) {
      var typing = /INPUT|TEXTAREA|SELECT/.test((e.target.tagName || "")) || e.target.isContentEditable;
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        box.hasAttribute("hidden") ? open() : close();
        return;
      }
      if (e.key === "/" && !typing && box.hasAttribute("hidden")) { e.preventDefault(); open(); return; }
      if (box.hasAttribute("hidden")) return;
      if (e.key === "Escape") { e.preventDefault(); close(); }
      else if (e.key === "ArrowDown") { e.preventDefault(); setCursor(cursor + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); setCursor(cursor - 1); }
      else if (e.key === "Tab") { e.preventDefault(); setCursor(cursor + (e.shiftKey ? -1 : 1)); }
      else if (e.key === "Enter") {
        var item = results[cursor];
        if (!item) return;
        e.preventDefault();
        if (item.run) { close(); item.run(); } else window.location.href = item.u;
      }
    });

    input.addEventListener("input", function () { render(input.value); });
    $$("[data-cmdk-close]", box).forEach(function (el) { el.addEventListener("click", close); });
    $$("[data-cmdk-open]").forEach(function (b) { b.addEventListener("click", open); });
  }

  /* ══ ambient: the running system behind every page ════════════════════
     A fixed canvas under the content: nodes drift and link when near,
     events travel along the links and land with a ripple, and code tokens
     rise and fade. Nodes and tokens scroll at different rates, so the page
     has depth. Colours are read from the --x-rgb tokens (again whenever the
     theme changes), strength is --net in CSS. Paused while the tab is hidden;
     under reduced motion it paints one still frame and stops. */
  function initAmbient() {
    var canvas = $("[data-ambient-net]");
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext("2d");
    // A planner's vocabulary: the network is a precedence diagram, the bars
    // are a Gantt chart drifting against its own baseline.
    var WORDS = ["WBS", "CPM", "TF = 0", "FS", "SS + 5d", "FF", "Lag 3d", "Baseline", "Data date",
      "P6", "MSP", "Critical path", "Float", "Milestone", "% Complete", "EOT", "TIA",
      "As-built", "As-planned", "Δ 12d", "SPI 0.94", "Gantt", "Look-ahead", "Recovery",
      "Delay", "ICB", "L3", "Window", "Update", "Progress"];
    var LINK = 150, POINTER = 180;
    var w = 0, h = 0, dpr = 1, colors = [], mono = "monospace";
    var nodes = [], glyphs = [], packets = [], ripples = [], bars = [];
    var pointer = { x: -1e4, y: -1e4 };
    var running = false, last = 0, nextPacket = 0;
    // On a touch device the network runs lighter: fewer nodes, ~30 frames a
    // second. It keeps running through a scroll — pausing it froze the
    // background under the finger and let it jump on release.
    var lite = !finePointer || window.innerWidth < 700;

    function rnd(a, b) { return a + Math.random() * (b - a); }
    function rgba(c, a) { return "rgba(" + colors[c] + "," + a.toFixed(3) + ")"; }
    function wrap(v, span) { return ((v % span) + span) % span; }
    // A point `p` (0..1) of the way along a link's elbow: across, then down.
    function along(k, p) {
      var hx = Math.abs(k.b.sx - k.a.sx), vy = Math.abs(k.b.sy - k.a.sy), total = hx + vy || 1;
      var d = Math.max(0, Math.min(1, p)) * total;
      if (d <= hx) return [k.a.sx + Math.sign(k.b.sx - k.a.sx) * d, k.a.sy];
      return [k.b.sx, k.a.sy + Math.sign(k.b.sy - k.a.sy) * (d - hx)];
    }

    function readColors() {
      var pal = readPalette();
      colors = HUES.map(function (hue) { return pal[hue]; });
      mono = pal.mono;
    }
    function makeNode() {
      return { x: rnd(0, w), y: rnd(0, h), vx: rnd(-.22, .22), vy: rnd(-.22, .22),
               r: rnd(1.6, 3.4), c: Math.floor(rnd(0, 4)), sx: 0, sy: 0, ms: Math.random() < .22 };
    }
    // One Gantt bar: a hollow baseline and the actual bar slipped a little
    // behind it, part filled with progress, a milestone at its finish.
    function makeBar(anywhere) {
      var len = rnd(70, 190);
      return { x: rnd(-40, w - len * .5), y: anywhere ? rnd(0, h) : h + 20, vy: -rnd(.05, .14),
               len: len, slip: rnd(0, len * .35), prog: rnd(.2, .9), c: Math.floor(rnd(0, 4)),
               age: anywhere ? rnd(0, 1) : 0, dur: rnd(14000, 24000) };
    }
    function makeGlyph(anywhere) {
      return { x: rnd(0, w), y: anywhere ? rnd(0, h) : h + 20, vy: -rnd(.12, .32),
               t: WORDS[Math.floor(rnd(0, WORDS.length))], c: Math.floor(rnd(0, 4)),
               size: Math.round(rnd(11, 17)), age: anywhere ? rnd(0, 1) : 0, dur: rnd(9000, 16000) };
    }
    function resize() {
      // A tab opened in the background can report a 0×0 viewport; wrapping
      // against 0 would park every node at NaN for good.
      // The canvas's own box, not innerHeight: it is sized in lvh, so a phone's
      // address bar coming and going changes nothing and is skipped here.
      var cw = canvas.clientWidth, ch = canvas.clientHeight;
      if (!cw || !ch || (cw === w && ch === h)) return;
      w = cw; h = ch;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
      var nodeCount = Math.round(Math.max(22, Math.min(lite ? 30 : 70, w * h / 21000)));
      var glyphCount = w < 700 ? 6 : 14;
      var barCount = w < 700 ? 3 : 7;
      while (bars.length < barCount) bars.push(makeBar(true));
      bars.length = barCount;
      while (nodes.length < nodeCount) nodes.push(makeNode());
      nodes.length = nodeCount;
      while (glyphs.length < glyphCount) glyphs.push(makeGlyph(true));
      glyphs.length = glyphCount;
      nodes.forEach(function (n) {
        n.x = isFinite(n.x) ? wrap(n.x, w) : rnd(0, w);
        n.y = isFinite(n.y) ? wrap(n.y, h) : rnd(0, h);
      });
      glyphs.forEach(function (g, i) { if (!isFinite(g.x) || g.x > w) glyphs[i] = makeGlyph(true); });
    }

    function step(dt, now) {
      nodes.forEach(function (n) {
        var dx = n.sx - pointer.x, dy = n.sy - pointer.y, d2 = dx * dx + dy * dy;
        if (d2 < 14400 && d2 > 1) { var f = (1 - Math.sqrt(d2) / 120) * .6; n.x += dx / Math.sqrt(d2) * f * dt; n.y += dy / Math.sqrt(d2) * f * dt; }
        n.x = wrap(n.x + n.vx * dt, w); n.y = wrap(n.y + n.vy * dt, h);
      });
      glyphs.forEach(function (g, i) {
        g.y += g.vy * dt; g.age += 16.67 * dt / g.dur;
        if (g.age >= 1) glyphs[i] = makeGlyph(true);
      });
      bars.forEach(function (b, i) {
        b.y += b.vy * dt; b.age += 16.67 * dt / b.dur;
        if (b.age >= 1) bars[i] = makeBar(true);
      });
      if (now > nextPacket) {
        nextPacket = now + rnd(260, 620);
        var a = nodes[Math.floor(rnd(0, nodes.length))];
        var near = nodes.filter(function (b) {
          var dx = a.sx - b.sx, dy = a.sy - b.sy; return b !== a && dx * dx + dy * dy < LINK * LINK;
        });
        if (near.length) packets.push({ a: a, b: near[Math.floor(rnd(0, near.length))], p: 0, v: rnd(.012, .022), c: a.c });
      }
      packets = packets.filter(function (k) {
        k.p += k.v * dt;
        if (k.p < 1) return true;
        if (k.torn) return false;
        ripples.push({ x: k.b.sx, y: k.b.sy, age: 0, c: k.c });
        return false;
      });
      ripples = ripples.filter(function (r) { r.age += .025 * dt; return r.age < 1; });
    }

    function draw() {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      var scroll = window.scrollY || 0;
      var i, j, n, m, dx, dy, d;
      for (i = 0; i < nodes.length; i++) { n = nodes[i]; n.sx = n.x; n.sy = wrap(n.y - scroll * .12, h); }

      ctx.lineWidth = 1;
      for (i = 0; i < nodes.length; i++) {
        n = nodes[i];
        for (j = i + 1; j < nodes.length; j++) {
          m = nodes[j]; dx = n.sx - m.sx; dy = n.sy - m.sy;
          if (dx * dx + dy * dy > LINK * LINK) continue;
          d = Math.sqrt(dx * dx + dy * dy);
          ctx.strokeStyle = rgba(n.c, (1 - d / LINK) * .45);
          ctx.beginPath(); ctx.moveTo(n.sx, n.sy); ctx.lineTo(m.sx, n.sy); ctx.lineTo(m.sx, m.sy); ctx.stroke();
        }
        dx = n.sx - pointer.x; dy = n.sy - pointer.y;
        if (dx * dx + dy * dy < POINTER * POINTER) {
          ctx.strokeStyle = rgba(n.c, (1 - Math.sqrt(dx * dx + dy * dy) / POINTER) * .6);
          ctx.beginPath(); ctx.moveTo(n.sx, n.sy); ctx.lineTo(pointer.x, pointer.y); ctx.stroke();
        }
      }

      // Activities are small boxes, milestones are diamonds.
      nodes.forEach(function (n) {
        var r = n.ms ? n.r * 1.5 : n.r;
        if (n.r > 2.6) { ctx.fillStyle = rgba(n.c, .14); ctx.fillRect(n.sx - r * 3, n.sy - r * 2, r * 6, r * 4); }
        ctx.fillStyle = rgba(n.c, .9);
        if (n.ms) {
          ctx.beginPath(); ctx.moveTo(n.sx, n.sy - r); ctx.lineTo(n.sx + r, n.sy);
          ctx.lineTo(n.sx, n.sy + r); ctx.lineTo(n.sx - r, n.sy); ctx.closePath(); ctx.fill();
        } else {
          ctx.fillRect(n.sx - r * 1.6, n.sy - r * .9, r * 3.2, r * 1.8);
        }
      });

      packets.forEach(function (k) {
        dx = k.b.sx - k.a.sx; dy = k.b.sy - k.a.sy;
        if (dx * dx + dy * dy > LINK * LINK * 1.5) { k.p = 2; k.torn = true; return; }   // a scroll wrap tore the link
        var head = along(k, k.p), x = head[0], y = head[1], t = Math.max(0, k.p - .22), q;
        ctx.strokeStyle = rgba(k.c, .7); ctx.lineWidth = 1.6;
        ctx.beginPath(); q = along(k, t); ctx.moveTo(q[0], q[1]);
        for (var s = 1; s <= 6; s++) { q = along(k, t + (k.p - t) * s / 6); ctx.lineTo(q[0], q[1]); }
        ctx.stroke();
        ctx.fillStyle = rgba(k.c, .22); ctx.beginPath(); ctx.arc(x, y, 6, 0, 6.283); ctx.fill();
        ctx.fillStyle = rgba(k.c, 1); ctx.beginPath(); ctx.arc(x, y, 2.2, 0, 6.283); ctx.fill();
      });
      ctx.lineWidth = 1.2;
      ripples.forEach(function (r) {
        ctx.strokeStyle = rgba(r.c, (1 - r.age) * .7);
        ctx.beginPath(); ctx.arc(r.x, r.y, 3 + r.age * 20, 0, 6.283); ctx.stroke();
      });

      ctx.lineWidth = 1;
      bars.forEach(function (b) {
        var a = Math.sin(Math.PI * Math.min(1, b.age)) * .75;
        var y = wrap(b.y - scroll * .2 + 30, h + 60) - 30, x = b.x, ax = x + b.slip, hgt = 7;
        ctx.strokeStyle = rgba(b.c, a * .55);
        ctx.strokeRect(x, y - hgt - 3, b.len, hgt * .6);                 // the baseline
        ctx.fillStyle = rgba(b.c, a * .28); ctx.fillRect(ax, y, b.len, hgt);
        ctx.fillStyle = rgba(b.c, a * .7);  ctx.fillRect(ax, y, b.len * b.prog, hgt);
        var mx = ax + b.len + 7, my = y + hgt / 2;                        // the finish milestone
        ctx.beginPath(); ctx.moveTo(mx, my - 4.5); ctx.lineTo(mx + 4.5, my);
        ctx.lineTo(mx, my + 4.5); ctx.lineTo(mx - 4.5, my); ctx.closePath(); ctx.fill();
      });

      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      if ("direction" in ctx) ctx.direction = "ltr";
      glyphs.forEach(function (g) {
        var a = Math.sin(Math.PI * Math.min(1, g.age)) * .8;
        ctx.font = "500 " + g.size + "px " + mono;
        ctx.fillStyle = rgba(g.c, a);
        ctx.fillText(g.t, g.x, wrap(g.y - scroll * .3 + 30, h + 60) - 30);
      });
    }

    function frame(now) {
      if (!running) return;
      if (lite && last && now - last < 32) { requestAnimationFrame(frame); return; }
      var dt = Math.min(48, now - (last || now)) / 16.67;
      last = now;
      step(dt, now);
      draw();
      requestAnimationFrame(frame);
    }
    function start() { if (running || reduceMotion) return; running = true; last = 0; requestAnimationFrame(frame); }
    function stop() { running = false; }

    readColors();
    resize();
    draw();
    draw();   // the first pass only placed the nodes on screen

    var resizeTimer;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () { resize(); if (!running) draw(); }, 120);
    });
    onThemeChange(function () { readColors(); if (!running) draw(); });

    if (reduceMotion) return;
    if (finePointer) {
      window.addEventListener("pointermove", function (e) { pointer.x = e.clientX; pointer.y = e.clientY; }, { passive: true });
      document.addEventListener("pointerleave", function () { pointer.x = pointer.y = -1e4; });
    }
    document.addEventListener("visibilitychange", function () { if (document.hidden) stop(); else start(); });
    start();
  }

  /* ══ build: the building the page puts up as it is read ═══════════════
     A second canvas over the network. The reader's scroll is the project's
     progress: at the top of a page there is a surveyed plot, by the foot of
     it a finished building has been handed over. In between, the work goes
     in the order a site does it — excavation and piles, then the frame floor
     by floor (columns, beams, slab) with a tower crane climbing beside it and
     sparks where the steel is going in, the façade following a few floors
     behind, level marks on each finished slab, the crane coming down after
     topping out, and the lights coming on at handover.

     The picture is a pure function of one number, `progress`, so scrolling
     back up takes the building down again and a restored scroll position
     shows the same building. That number eases toward the scroll position
     and the loop stops once it arrives: nothing runs while the page is still.
     Geometry is laid out left-to-right and mirrored for RTL, so the building
     stands at the inline end in every language; labels are drawn unmirrored.
     Strength is --build in CSS. Under reduced motion the finished building
     is drawn once and does not follow the scroll. */
  function initBuild() {
    var canvas = $("[data-ambient-build]");
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext("2d");
    var rtl = document.body.getAttribute("dir") === "rtl";
    var pal = readPalette();
    var w = 0, h = 0, dpr = 1, L = null;
    var progress = 0, goal = 0, running = false, last = 0, sparks = [], face = null;
    var TAU = 6.283;

    function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
    // Where `v` sits inside the stretch a..b, as 0..1. Every stage of the
    // work is one such window on the single progress number.
    function seg(v, a, b) { return clamp01((v - a) / (b - a)); }
    function ease(t) { return t * t * (3 - 2 * t); }
    function rgba(hue, a) { return "rgba(" + pal[hue] + "," + clamp01(a).toFixed(3) + ")"; }
    // A fixed 0..1 per window, so the lights come on in the same scattered
    // order every time rather than flickering from frame to frame.
    function hash(i, j) { var s = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return s - Math.floor(s); }

    // Geometry is drawn in LTR coordinates; in RTL this transform mirrors it.
    function geo() { ctx.setTransform(rtl ? -dpr : dpr, 0, 0, dpr, rtl ? w * dpr : 0, 0); }
    function label(text, x, y, align, hue, a, size) {
      if (a <= .01) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.font = "500 " + size + "px " + pal.mono;
      ctx.fillStyle = rgba(hue, a);
      ctx.textAlign = !rtl || align === "center" ? align : align === "left" ? "right" : "left";
      ctx.fillText(text, rtl ? w - x : x, y);
      geo();
    }
    function line(x1, y1, x2, y2) { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); }
    function diamond(x, y, r) {
      ctx.beginPath(); ctx.moveTo(x, y - r); ctx.lineTo(x + r, y); ctx.lineTo(x, y + r); ctx.lineTo(x - r, y);
      ctx.closePath(); ctx.fill();
    }

    function layout() {
      // A background tab can report a 0×0 viewport; keep the last layout.
      // Measured on the canvas (lvh), so the address bar never re-lays it out.
      var cw = canvas.clientWidth, ch = canvas.clientHeight;
      if (!cw || !ch || (L && cw === w && ch === h)) return;
      w = cw; h = ch;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
      var narrow = w < 700;
      var fh = Math.max(18, Math.min(38, h * .045, w * .07));          // one storey
      var bays = narrow ? 3 : 4, bw = Math.round(fh * 1.35);
      var ground = h - Math.max(28, h * .07);
      // As many storeys as fit under the crane's head room, within reason.
      var floors = Math.max(4, Math.min(narrow ? 9 : 12, Math.floor((ground - h * .14) / fh) - 3));
      var mast = w - Math.max(34, w * .05);
      L = { fh: fh, bays: bays, bw: bw, W: bays * bw, G: ground, N: floors, x0: mast - 30 - bays * bw, mast: mast };
    }
    // The top of the page is not an empty field: the plot is already set out.
    function scrolled() {
      var max = root.scrollHeight - window.innerHeight;
      return max > 40 ? .05 + .95 * clamp01((window.scrollY || 0) / max) : 1;
    }

    function draw() {
      if (!L) return;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      geo();
      if ("direction" in ctx) ctx.direction = "ltr";
      ctx.textBaseline = "middle";
      var p = progress, fh = L.fh, bw = L.bw, W = L.W, G = L.G, N = L.N, x0 = L.x0, mast = L.mast;
      // The stages, as windows on progress. The façade's window starts later
      // and runs longer than the frame's, so it always trails a few storeys.
      var site = ease(seg(p, 0, .06)), dig = seg(p, .03, .13), frame = seg(p, .1, .72) * N,
          skin = seg(p, .3, .9) * N, lights = seg(p, .86, 1), roof = ease(seg(p, .72, .78)),
          handover = ease(seg(p, .95, 1)), crane = ease(seg(p, .06, .12)) * (1 - ease(seg(p, .82, .9)));
      var cx = x0 + W / 2, i, j, k, x;

      // ── the plot: ground line, earth hatch, setting-out pegs ──
      var half = (W / 2 + 90) * site;
      ctx.lineWidth = 1.2; ctx.strokeStyle = rgba("sky", .75 * site);
      line(cx - half, G, cx + half, G);
      ctx.lineWidth = 1; ctx.strokeStyle = rgba("sky", .3 * site);
      for (x = cx - half + 4; x < cx + half; x += 9) line(x, G + 2, x - 6, G + 8);
      var pegs = site * (1 - dig);
      if (pegs > .01) {
        ctx.setLineDash([3, 4]); ctx.strokeStyle = rgba("sky", .6 * pegs);
        line(x0, G, x0, G - fh * 2.2); line(x0 + W, G, x0 + W, G - fh * 2.2);
        line(x0 - 14, G - fh * 1.6, x0 + W + 14, G - fh * 1.6);
        ctx.setLineDash([]); ctx.fillStyle = rgba("peach", .9 * pegs);
        diamond(x0, G - fh * 2.2, 3.5); diamond(x0 + W, G - fh * 2.2, 3.5);
      }

      // ── below ground: piles, then pile caps and the raft ──
      if (dig > 0) {
        var pile = Math.min(h - G - 6, fh * 1.6) * ease(seg(dig, 0, .6));
        ctx.setLineDash([2, 3]); ctx.strokeStyle = rgba("mint", .55);
        for (i = 0; i <= L.bays; i++) line(x0 + i * bw, G, x0 + i * bw, G + pile);
        ctx.setLineDash([]);
        var cap = seg(dig, .5, 1);
        ctx.fillStyle = rgba("mint", .8 * cap);
        for (i = 0; i <= L.bays; i++) ctx.fillRect(x0 + i * bw - 5, G - 2, 10, 5);
        ctx.fillStyle = rgba("mint", .35 * cap); ctx.fillRect(x0 - 6, G - 2, (W + 12) * cap, 3);
      }

      // ── the frame, storey by storey: columns rise, the beam runs across,
      //    the slab is cast; one braced core bay stiffens every storey ──
      var core = L.bays > 3 ? 1 : 0, work = null;
      for (k = 0; k < N; k++) {
        var fk = clamp01(frame - k);
        if (fk <= 0) break;
        var yb = G - k * fh, yt = yb - fh;
        var col = ease(seg(fk, 0, .45)), beam = ease(seg(fk, .4, .8)), slab = seg(fk, .7, 1);
        ctx.lineWidth = 1.6; ctx.strokeStyle = rgba("mint", .85);
        for (i = 0; i <= L.bays; i++) line(x0 + i * bw, yb, x0 + i * bw, yb - fh * col);
        if (beam > 0) { ctx.lineWidth = 1.8; line(x0, yt, x0 + W * beam, yt); }
        if (slab > 0) {
          ctx.fillStyle = rgba("mint", .45 * slab); ctx.fillRect(x0 - 4, yt - 1.5, W + 8, 3);
          ctx.lineWidth = 1; ctx.strokeStyle = rgba("sky", .4 * slab);
          line(x0 + core * bw, yb, x0 + (core + 1) * bw, yt); line(x0 + (core + 1) * bw, yb, x0 + core * bw, yt);
        }
        if (fk < 1) work = { x: beam > 0 ? x0 + W * beam : x0 + bw * L.bays * (k % 2), y: beam > 0 ? yt : yb - fh * col };
        // level marks on each cast slab (every other one when storeys are short)
        if (slab > 0 && (fh >= 26 || k % 2)) {
          ctx.fillStyle = rgba("sky", .7 * slab);
          ctx.beginPath(); ctx.moveTo(x0 - 10, yt); ctx.lineTo(x0 - 16, yt - 5); ctx.lineTo(x0 - 4, yt - 5); ctx.closePath(); ctx.fill();
          label("+" + ((k + 1) * 3.2).toFixed(2), x0 - 20, yt - 3, "right", "sky", .75 * slab, 10);
        }
      }
      label("± 0.00", x0 - 20, G - 3, "right", "sky", .75 * site, 10);

      // ── the façade: glazed panels bay by bay, then the lights ──
      for (k = 0; k < N; k++) {
        var sk = Math.min(clamp01(skin - k), clamp01(frame - k));
        if (sk <= 0) break;
        var top = G - (k + 1) * fh;
        for (j = 0; j < L.bays; j++) {
          var pj = ease(seg(sk, j / L.bays, (j + 1) / L.bays));
          if (pj <= 0) break;
          var px = x0 + j * bw + 3, py = top + 3, pw = bw - 6, ph = fh - 6;
          ctx.fillStyle = rgba("sky", .16 * pj); ctx.fillRect(px, py, pw, ph * pj);
          ctx.lineWidth = 1; ctx.strokeStyle = rgba("sky", .5 * pj); ctx.strokeRect(px, py, pw, ph * pj);
          ctx.strokeStyle = rgba("sky", .3 * pj); line(px + pw / 2, py, px + pw / 2, py + ph * pj);
          // About two windows in three, never the braced core (it is the stair).
          var on = j === core ? 0 : clamp01((lights * .75 - hash(k, j)) / .08);
          if (on > 0 && pj >= 1) {
            ctx.fillStyle = rgba("peach", .12 * on); ctx.fillRect(px - 2, py - 2, pw + 4, ph + 4);
            ctx.fillStyle = rgba("peach", .42 * on); ctx.fillRect(px + 2, py + 2, pw - 4, ph - 4);
          }
        }
      }

      // ── topping out, then handover ──
      var roofY = G - N * fh;
      if (roof > 0) {
        ctx.lineWidth = 1.4; ctx.strokeStyle = rgba("mint", .8 * roof);
        line(x0 - 4, roofY - 6, x0 - 4 + (W + 8) * roof, roofY - 6);
        ctx.lineWidth = 1; ctx.strokeRect(x0 + bw * .6, roofY - 6 - fh * .45 * roof, bw * .9, fh * .45 * roof);
        label("Topping out", cx, roofY - fh * 1.1, "center", "mint", .8 * roof * (1 - handover), 10);
      }
      if (handover > 0) {
        var fx = x0 + W - bw * .6, ft = roofY - 6 - fh * 1.3 * handover;
        ctx.lineWidth = 1; ctx.strokeStyle = rgba("peach", .9 * handover); line(fx, roofY - 6, fx, ft);
        ctx.fillStyle = rgba("peach", .85 * handover);
        ctx.beginPath(); ctx.moveTo(fx, ft); ctx.lineTo(fx - 14 * handover, ft + 5); ctx.lineTo(fx, ft + 10); ctx.closePath(); ctx.fill();
        diamond(cx, roofY - fh * 1.1, 5 * handover);
        label("Handover", cx, roofY - fh * 1.1 - 14, "center", "peach", .9 * handover, 11);
      }

      // ── the tower crane: it climbs two storeys ahead of the frame, carries
      //    the next member to the working face, and comes down after topping out ──
      if (crane > .01) {
        var ahead = G - Math.min(frame + 2.4, N + 2.4) * fh;
        var mt = G - (G - Math.min(G - fh * 3, ahead)) * crane, jib = W + 24, a = Math.min(1, crane * 1.5);
        ctx.lineWidth = 1; ctx.strokeStyle = rgba("peach", .75 * a);
        line(mast - 3, G, mast - 3, mt); line(mast + 3, G, mast + 3, mt);
        ctx.strokeStyle = rgba("peach", .4 * a);
        ctx.beginPath(); ctx.moveTo(mast - 3, G);
        for (var y = G, s = 1; y > mt; y -= 7, s = -s) ctx.lineTo(mast + 3 * s, Math.max(mt, y - 7));
        ctx.stroke();
        ctx.strokeStyle = rgba("peach", .8 * a); ctx.lineWidth = 1.2;
        line(mast + fh * 1.2, mt, mast - jib, mt); line(mast + fh * 1.2, mt + 3, mast - jib, mt + 3);
        ctx.lineWidth = 1; ctx.strokeStyle = rgba("peach", .5 * a);
        line(mast, mt - fh * .9, mast - jib, mt); line(mast, mt - fh * .9, mast + fh * 1.2, mt); line(mast, mt, mast, mt - fh * .9);
        ctx.fillStyle = rgba("peach", .7 * a);
        ctx.fillRect(mast + fh * .75, mt, 9, 7);                          // counterweight
        ctx.fillRect(mast - 6, mt + 3, 8, 6);                             // cab
        // The trolley shuttles across the storey being built; its phase is
        // that storey's own progress, so it is continuous from one to the next.
        var building = frame < N;
        var tx = Math.max(mast - jib + 6, x0 + W * (.5 - .5 * Math.cos((frame % 1) * TAU)));
        var storeyTop = G - Math.min(Math.floor(frame) + 1, N) * fh;
        var hy = building ? Math.max(mt + 14, storeyTop - 12) : mt + 14;
        ctx.fillRect(tx - 4, mt + 2, 8, 3);
        ctx.strokeStyle = rgba("peach", .55 * a); line(tx, mt + 5, tx, hy);
        if (building) {
          ctx.fillStyle = rgba("mint", .7 * a); ctx.fillRect(tx - bw * .35, hy + 5, bw * .7, 3);
          line(tx, hy, tx - bw * .3, hy + 5); line(tx, hy, tx + bw * .3, hy + 5);
        }
      }

      // ── sparks at the working face, only while work is going on ──
      face = work;
      ctx.fillStyle = rgba("peach", 1);
      sparks.forEach(function (s) { ctx.globalAlpha = s.life; ctx.fillRect(s.x - .9, s.y - .9, 1.8, 1.8); });
      ctx.globalAlpha = 1;

      // ── the progress readout, as a planner would print it under the drawing ──
      var storey = Math.min(N, Math.floor(frame) + 1);
      label(handover >= 1 ? "Handover · 100%" : "L" + (storey < 10 ? "0" : "") + storey + " · " + Math.round(p * 100) + "%",
            cx, G + 18, "center", "sky", .8 * site, 10);
    }

    function tick(now) {
      var dt = Math.min(48, now - (last || now)) / 16.67;
      last = now;
      progress += (goal - progress) * (1 - Math.pow(.88, dt));
      if (Math.abs(goal - progress) < .0004) progress = goal;
      // the working face drawn last frame, while the building is moving
      if (face && Math.abs(goal - progress) > .002 && sparks.length < 40) {
        sparks.push({ x: face.x, y: face.y, vx: (Math.random() - .5) * 2.4, vy: -Math.random() * 1.8, life: 1 });
      }
      sparks = sparks.filter(function (s) {
        s.x += s.vx * dt; s.y += s.vy * dt; s.vy += .12 * dt; s.life -= .035 * dt; return s.life > 0;
      });
      draw();
      if (progress !== goal || sparks.length) requestAnimationFrame(tick);
      else running = false;
    }
    function follow() {
      goal = scrolled();
      if (running || goal === progress) return;
      running = true; last = 0;
      requestAnimationFrame(tick);
    }

    layout();
    if (reduceMotion) {
      progress = goal = 1;
      draw();
      window.addEventListener("resize", function () { layout(); draw(); });
      onThemeChange(function () { pal = readPalette(); draw(); });
      return;
    }
    draw();
    follow();                          // the first visit watches the plot get set out
    window.addEventListener("scroll", follow, { passive: true });
    var resizeTimer;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () { layout(); draw(); follow(); }, 120);
    });
    // Images and fonts arriving change the page's length, and so the goal.
    if (window.ResizeObserver) new ResizeObserver(follow).observe(document.body);
    onThemeChange(function () { pal = readPalette(); if (!running) draw(); });
  }

  /* ══ boot ══════════════════════════════════════════════════════════════ */
  function boot() {
    initTheme();
    initAmbient();
    initBuild();
    initHeader();
    initNavIndicator();
    initPopovers();
    initTips();
    initReveal();
    initPointer();
    initFilter();
    initCopy();
    initShare();
    initForms();
    initPalette();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
