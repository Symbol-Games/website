// Symbol Interactive: the few things on the pages that move. Nothing loads from elsewhere, and every page reads fine without this file.
(function () {
  "use strict";
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Zar's eyes follow the visitor and blink now and then. The pupils rest where the logo draws them.
  var zars = Array.prototype.slice.call(document.querySelectorAll(".zar:not(.asleep)"));
  if (zars.length && !still) {
    var pupils = zars.map(function (z) { return z.querySelectorAll(".z-pup"); });
    var tx = .55, ty = .15, x = tx, y = ty, last = -1e9;
    var onScreen = function () {
      for (var i = 0; i < zars.length; i++) {
        var r = zars[i].getBoundingClientRect();
        if (r.width > 40 && r.bottom > 0 && r.top < innerHeight) return r;
      }
      return null;
    };
    addEventListener("pointermove", function (e) {
      var r = onScreen();
      if (!r) return;
      var dx = e.clientX - (r.left + r.width * .5), dy = e.clientY - (r.top + r.height * .26), d = Math.hypot(dx, dy) || 1, k = Math.min(1, d / 280);
      tx = dx / d * k; ty = dy / d * k; last = performance.now();
    }, { passive: true });
    var frame = function (t) {
      if (t - last > 4200) { tx = .55 + Math.sin(t / 2100) * .3; ty = .15 + Math.sin(t / 1500) * .25; }
      x += (tx - x) * .15; y += (ty - y) * .15;
      var m = "translate(" + (x * 36 - 22).toFixed(1) + "px," + (y * 36 - 6).toFixed(1) + "px)";
      for (var i = 0; i < pupils.length; i++) for (var j = 0; j < pupils[i].length; j++) pupils[i][j].style.transform = m;
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
    var blink = function () {
      setTimeout(function () {
        zars.forEach(function (z) { z.classList.add("blink"); });
        setTimeout(function () { zars.forEach(function (z) { z.classList.remove("blink"); }); }, 120);
        blink();
      }, 2700 + Math.random() * 3600);
    };
    blink();
  }

  // The menu printed on the hero card scrolls away with the card; the bar at the top of the window takes over until the card is back.
  var floatBar = document.getElementById("floatbar"), cardBar = document.querySelector(".bar");
  if (floatBar && cardBar && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) { floatBar.classList.toggle("show", !entries[0].isIntersecting); }).observe(cardBar);
  }

  // The sky guide's calendar marks this month.
  var month = document.querySelector('[data-month="' + (new Date().getMonth() + 1) + '"]');
  if (month) month.classList.add("now");

  // The packaging opens with a click.
  var pack = document.getElementById("blister");
  if (pack) pack.addEventListener("click", function () {
    var open = pack.classList.toggle("open");
    pack.setAttribute("aria-label", open ? pack.dataset.shut : pack.dataset.open);
  });

  // Short clips play only while they are on screen, and never under reduced motion. One button pauses them all. The trailer has its own controls.
  var clips = Array.prototype.slice.call(document.querySelectorAll("video.auto")), toggle = document.getElementById("clips-toggle");
  if (clips.length && !still && "IntersectionObserver" in window) {
    var held = false, inView = new Set();
    var run = function (v) { var p = v.play(); if (p) p.catch(function () {}); };
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { inView.add(e.target); if (!held) run(e.target); } else { inView.delete(e.target); e.target.pause(); }
      });
    }, { threshold: .25 });
    clips.forEach(function (v) { v.muted = true; seen.observe(v); });
    if (toggle) {
      toggle.hidden = false;
      toggle.addEventListener("click", function () {
        held = !held;
        toggle.textContent = held ? toggle.dataset.play : toggle.dataset.pause;
        if (held) clips.forEach(function (v) { v.pause(); }); else inView.forEach(run);
      });
    }
  }

  // The demo: in the phone on the page when the phone is big enough to play in and fits the window, otherwise full screen in a dialog.
  // No request until asked; without this script the button is a plain link. The demo has music, so it ends with its button or when scrolled away.
  var device = document.getElementById("device"), box = document.getElementById("demo-box"), inBox = document.getElementById("demo-frame"), close = document.getElementById("demo-close"), stop = document.getElementById("demo-stop");
  var resting = null, away = null;
  var makeFrame = function (a) {
    var f = document.createElement("iframe");
    f.src = a.getAttribute("href"); f.title = a.dataset.title || ""; f.allow = "autoplay";
    return f;
  };
  var endDemo = function () {
    if (inBox) inBox.textContent = "";
    if (box && box.open) box.close();
    document.documentElement.style.overflow = "";
    if (resting) { device.replaceChildren.apply(device, resting); resting = null; }
    if (stop) stop.hidden = true;
    if (away) { away.disconnect(); away = null; }
  };
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-demo]");
    if (!a) return;
    if (device && device.clientWidth >= 280 && device.offsetHeight <= innerHeight - 16 - (floatBar ? floatBar.offsetHeight : 0)) {
      e.preventDefault();
      resting = Array.prototype.slice.call(device.childNodes);
      device.replaceChildren(makeFrame(a));
      if (stop) stop.hidden = false;
      device.scrollIntoView({ block: "nearest" });
      if ("IntersectionObserver" in window) {
        var seenOnce = false;  // the first report can arrive before the scroll lands
        away = new IntersectionObserver(function (entries) {
          if (entries[0].isIntersecting) seenOnce = true; else if (seenOnce) endDemo();
        });
        away.observe(device);
      }
    } else if (box && box.showModal) {
      e.preventDefault();
      inBox.textContent = "";
      inBox.appendChild(makeFrame(a));
      document.documentElement.style.overflow = "hidden";
      box.showModal();
    }
  });
  if (close) close.addEventListener("click", endDemo);
  if (stop) stop.addEventListener("click", endDemo);
  if (box) box.addEventListener("close", endDemo);
  addEventListener("message", function (e) { if (e.origin === location.origin && e.data === "sj-demo-close") endDemo(); });
})();
