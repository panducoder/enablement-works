/* The Shift (enablement.works/shift/): progressive enhancement only.
   Every page is complete without this file. No cookies, storage or tracking. */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return false; });
    }
    return Promise.resolve(false);
  }
  function flash(el, text, ms) {
    if (!el) return;
    var old = el.getAttribute("data-label") || el.textContent;
    el.setAttribute("data-label", old);
    el.textContent = text;
    setTimeout(function () { el.textContent = old; }, ms || 1800);
  }

  /* ---------------------------------------------------------------- scroll film */
  var film = document.querySelector("[data-film]");
  if (film) {
    var video = film.querySelector("video");
    var bar = film.querySelector(".film__progress");
    var chapters = Array.prototype.slice.call(film.querySelectorAll(".film__chapter"));
    var routeBtns = Array.prototype.slice.call(film.querySelectorAll(".film__route button"));
    var duration = 0, target = 0, raf = 0, active = -1;

    var progress = function () {
      var rect = film.getBoundingClientRect();
      var span = film.offsetHeight - window.innerHeight;
      return Math.min(1, Math.max(0, -rect.top / Math.max(span, 1)));
    };
    var paint = function () {
      raf = 0;
      var p = progress();
      if (bar) bar.style.setProperty("--p", p.toFixed(4));
      var idx = Math.min(chapters.length - 1, Math.floor(p * chapters.length));
      if (idx !== active) {
        active = idx;
        routeBtns.forEach(function (b, i) { if (i === idx) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current"); });
      }
      if (duration) {
        target = p * (duration - 0.05);
        if (!video.seeking && Math.abs(video.currentTime - target) > 0.02) video.currentTime = target;
      }
    };
    var schedule = function () { if (!raf) raf = requestAnimationFrame(paint); };
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
    routeBtns.forEach(function (b, i) {
      b.addEventListener("click", function () {
        var span = film.offsetHeight - window.innerHeight;
        var top = film.getBoundingClientRect().top + window.scrollY + span * ((i + 0.02) / chapters.length);
        window.scrollTo({ top: top, behavior: reduce ? "auto" : "smooth" });
      });
    });
    paint();

    if (!reduce && video && window.fetch && window.URL) {
      var small = window.matchMedia("(max-width: 860px)").matches;
      var src = small ? video.getAttribute("data-src-mobile") : video.getAttribute("data-src");
      fetch(src).then(function (r) { if (!r.ok) throw new Error(r.status); return r.blob(); }).then(function (blob) {
        var url = URL.createObjectURL(blob);
        video.addEventListener("loadedmetadata", function () {
          duration = video.duration || 0;
          video.addEventListener("seeked", function () {
            film.setAttribute("data-ready", "true");
            if (Math.abs(video.currentTime - target) > 0.02) video.currentTime = target;
          });
          paint();
          if (!video.currentTime) video.currentTime = 0.001;
        }, { once: true });
        video.src = url;
        window.addEventListener("pagehide", function () { URL.revokeObjectURL(url); }, { once: true });
      }).catch(function () { /* poster stays; the story is fully readable */ });
    }
  }

  /* ---------------------------------------------------------------- seam */
  var seam = document.querySelector("[data-seam]");
  if (seam) {
    var range = seam.querySelector(".seam__range");
    var setSeam = function (v) { seam.style.setProperty("--seam", v + "%"); range.value = Math.round(v); };
    range.addEventListener("input", function () { setSeam(Number(range.value)); });
    var cases = JSON.parse(document.getElementById("seam-cases").textContent);
    var btns = Array.prototype.slice.call(document.querySelectorAll(".seamcases button"));
    var bt = seam.querySelector("[data-before]"), at = seam.querySelector("[data-after]"), watch = document.querySelector(".seamwatch");
    btns.forEach(function (b, i) {
      b.addEventListener("click", function () {
        btns.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        [bt, at].forEach(function (el) { el.classList.remove("is-new"); void el.offsetWidth; el.classList.add("is-new"); });
        bt.textContent = cases[i].before; at.textContent = cases[i].after; watch.href = cases[i].href;
      });
    });
    if (!reduce && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        if (!entries.some(function (e) { return e.isIntersecting; })) return;
        io.disconnect();
        var start = 0;
        var step = function (now) {
          if (!start) start = now;
          var p = Math.min(1, (now - start) / 1500), e = 1 - Math.pow(1 - p, 4);
          setSeam(90 - 40 * e);
          if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }, { threshold: 0.4 });
      io.observe(seam);
    }
  }

  /* ---------------------------------------------------------------- impact board */
  var board = document.querySelector("[data-board]");
  if (board) {
    var FACETS = JSON.parse(document.getElementById("board-facets").textContent);
    var list = board.querySelector(".ledger");
    var rows = Array.prototype.slice.call(list.querySelectorAll(".srow"));
    var base = board.getAttribute("data-base");

    var read = function () {
      var q = new URLSearchParams(location.search), s = {};
      FACETS.forEach(function (f) { s[f.key] = (q.get(f.key) || "").split(",").filter(Boolean); });
      s.q = (q.get("q") || "").trim();
      s.sort = q.get("sort") || "shift";
      return s;
    };
    var href = function (s) {
      var q = new URLSearchParams();
      FACETS.forEach(function (f) { if (s[f.key].length) q.set(f.key, s[f.key].join(",")); });
      if (s.q) q.set("q", s.q);
      if (s.sort && s.sort !== "shift") q.set("sort", s.sort);
      var str = q.toString().replace(/%2C/g, ",");
      return base + (str ? "?" + str : "");
    };
    var clone = function (s) { var c = { q: s.q, sort: s.sort }; FACETS.forEach(function (f) { c[f.key] = s[f.key].slice(); }); return c; };
    var matches = function (row, s, skip) {
      for (var i = 0; i < FACETS.length; i++) {
        var f = FACETS[i];
        if (f.key === skip || !s[f.key].length) continue;
        var vals = (row.getAttribute("data-" + f.key) || "").split(" ");
        if (!s[f.key].some(function (v) { return vals.indexOf(v) >= 0; })) return false;
      }
      if (s.q) {
        var hay = row.getAttribute("data-hay");
        if (!s.q.toLowerCase().split(/\s+/).every(function (w) { return hay.indexOf(w) >= 0; })) return false;
      }
      return true;
    };
    var fmt = function (h) { return h <= 0 ? "0" : h >= 10 ? String(Math.round(h)) : h.toFixed(1).replace(/\.0$/, ""); };

    var render = function () {
      var s = read();
      var shown = rows.filter(function (r) { return matches(r, s); });
      var key = s.sort === "hours" ? "hours" : s.sort === "newest" ? "published" : "mult";
      shown.sort(function (a, b) {
        if (key === "published") return b.getAttribute("data-published").localeCompare(a.getAttribute("data-published"));
        return Number(b.getAttribute("data-" + key)) - Number(a.getAttribute("data-" + key)) || Number(b.getAttribute("data-mult")) - Number(a.getAttribute("data-mult"));
      });
      rows.forEach(function (r) { r.hidden = shown.indexOf(r) < 0; });
      shown.forEach(function (r, i) { list.appendChild(r); r.querySelector(".srow__rank").textContent = (i + 1 < 10 ? "0" : "") + (i + 1); });
      board.querySelector(".board__empty").hidden = shown.length > 0;
      list.hidden = shown.length === 0;
      var hours = shown.reduce(function (t, r) { return t + Number(r.getAttribute("data-hours")); }, 0);
      board.querySelector("[data-sum-hours]").firstChild.nodeValue = fmt(hours);
      board.querySelector("[data-count]").textContent = shown.length;
      board.querySelector(".board__count").textContent = shown.length + (shown.length === 1 ? " workflow" : " workflows") + (s.q ? " matching “" + s.q + "”" : "");

      Array.prototype.forEach.call(board.querySelectorAll(".fchip"), function (chip) {
        var k = chip.getAttribute("data-facet"), v = chip.getAttribute("data-value");
        var on = s[k].indexOf(v) >= 0;
        var next = clone(s);
        next[k] = on ? next[k].filter(function (x) { return x !== v; }) : next[k].concat(v);
        chip.href = href(next);
        chip.setAttribute("aria-pressed", String(on));
        var n = rows.filter(function (r) { return matches(r, s, k) && (r.getAttribute("data-" + k) || "").split(" ").indexOf(v) >= 0; }).length;
        chip.querySelector("small").textContent = n;
        if (!on && n === 0) chip.setAttribute("data-empty", "true"); else chip.removeAttribute("data-empty");
      });
      Array.prototype.forEach.call(board.querySelectorAll(".sorter a"), function (a) {
        var next = clone(s); next.sort = a.getAttribute("data-sort");
        a.href = href(next);
        a.setAttribute("aria-pressed", String(a.getAttribute("data-sort") === s.sort));
      });
      var active = board.querySelector(".ssum__active"), hint = board.querySelector(".ssum__hint");
      active.innerHTML = "";
      FACETS.forEach(function (f) {
        s[f.key].forEach(function (v) {
          var label = (f.values.filter(function (x) { return x[0] === v; })[0] || [v, v])[1];
          var next = clone(s); next[f.key] = next[f.key].filter(function (x) { return x !== v; });
          var li = document.createElement("li"), a = document.createElement("a");
          a.href = href(next); a.textContent = label + " ×"; a.setAttribute("aria-label", "Remove filter " + label);
          li.appendChild(a); active.appendChild(li);
        });
      });
      hint.hidden = active.children.length > 0;
      var input = board.querySelector("#board-q");
      if (document.activeElement !== input) input.value = s.q;
      Array.prototype.forEach.call(board.querySelectorAll(".board__search input[type=hidden]"), function (h) { h.remove(); });
      var form = board.querySelector(".board__search");
      FACETS.forEach(function (f) {
        if (!s[f.key].length) return;
        var h = document.createElement("input"); h.type = "hidden"; h.name = f.key; h.value = s[f.key].join(","); form.appendChild(h);
      });
      if (s.sort !== "shift") { var h2 = document.createElement("input"); h2.type = "hidden"; h2.name = "sort"; h2.value = s.sort; form.appendChild(h2); }
    };

    board.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a.fchip, .sorter a, .ssum__active a, .board__empty a");
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      history.pushState(null, "", a.getAttribute("href"));
      render();
    });
    window.addEventListener("popstate", render);
    var copyBtn = board.querySelector(".ssum__copy");
    copyBtn.addEventListener("click", function () {
      copyText(location.href).then(function (ok) { flash(copyBtn, ok ? "View link copied" : "Copy the address bar"); });
    });
    render();
  }

  /* ---------------------------------------------------------------- video page */
  var player = document.querySelector("[data-player]");
  if (player) {
    var v = player.querySelector("video");
    var marks = Array.prototype.slice.call(player.querySelectorAll(".chapters button"));
    var moment = player.querySelector(".moment");
    var canonical = player.getAttribute("data-url");
    var t0 = Number(new URLSearchParams(location.search).get("t"));
    if (t0 > 0) {
      var seek = function () { v.currentTime = Math.min(t0, Math.max(0, (v.duration || t0) - 0.1)); };
      if (v.readyState >= 1) seek(); else v.addEventListener("loadedmetadata", seek, { once: true });
    }
    var clock = function (t) { t = Math.max(0, Math.floor(t)); return Math.floor(t / 60) + ":" + (t % 60 < 10 ? "0" : "") + (t % 60); };
    v.addEventListener("timeupdate", function () {
      var now = v.currentTime;
      marks.forEach(function (b, i) {
        var at = Number(b.getAttribute("data-at")), next = marks[i + 1] ? Number(marks[i + 1].getAttribute("data-at")) : Infinity;
        if (now >= at && now < next) b.setAttribute("aria-current", "true"); else b.removeAttribute("aria-current");
      });
      moment.textContent = "Share this moment at " + clock(now);
    });
    marks.forEach(function (b) {
      b.addEventListener("click", function () { v.currentTime = Number(b.getAttribute("data-at")); v.play().catch(function () {}); });
    });
    moment.addEventListener("click", function () {
      var t = Math.floor(v.currentTime);
      copyText(canonical + (t ? "?t=" + t : "")).then(function (ok) { flash(moment, ok ? "Link copied" : canonical + "?t=" + t); });
    });
  }

  var steal = document.querySelector(".steal");
  if (steal) {
    steal.addEventListener("click", function () {
      var pre = document.querySelector(".move pre");
      copyText(pre.textContent).then(function (ok) {
        if (ok) { flash(steal, "Copied. Go sell.", 2200); return; }
        var r = document.createRange(); r.selectNodeContents(pre);
        var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
        flash(steal, "Selected. Press copy.", 2200);
      });
    });
  }

  var share = document.querySelector("[data-share]");
  if (share) {
    var status = share.querySelector(".sharebox__status");
    var say = function (t) { status.textContent = t; setTimeout(function () { status.textContent = ""; }, 2000); };
    share.querySelector("[data-copy-link]").addEventListener("click", function () {
      var url = share.getAttribute("data-url");
      copyText(url).then(function (ok) { say(ok ? "Link copied" : url); });
    });
    var embedBtn = share.querySelector("[data-embed-toggle]"), box = share.querySelector(".sharebox__embed");
    embedBtn.addEventListener("click", function () {
      box.hidden = !box.hidden;
      embedBtn.setAttribute("aria-expanded", String(!box.hidden));
    });
    box.querySelector("button").addEventListener("click", function () {
      var code = box.querySelector("textarea").value;
      copyText(code).then(function (ok) { say(ok ? "Embed code copied" : "Select the code and copy it"); });
    });
  }
})();
