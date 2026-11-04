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

  // The packaging opens with a click.
  var pack = document.getElementById("blister");
  if (pack) pack.addEventListener("click", function () {
    var open = pack.classList.toggle("open");
    pack.setAttribute("aria-pressed", String(open));
    pack.setAttribute("aria-label", open ? pack.dataset.shut : pack.dataset.open);
  });

  // Short clips play only while they are on screen, and never under reduced motion. The trailer has its own controls.
  var clips = document.querySelectorAll("video.auto");
  if (clips.length && !still && "IntersectionObserver" in window) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { var p = e.target.play(); if (p) p.catch(function () {}); } else e.target.pause();
      });
    }, { threshold: .25 });
    Array.prototype.forEach.call(clips, function (v) { v.muted = true; seen.observe(v); });
  }

  // The demo: in the phone on the page on a wide screen, full screen in a dialog on a small one. No request until asked; without this script the button is a plain link.
  var device = document.getElementById("device"), box = document.getElementById("demo-box"), inBox = document.getElementById("demo-frame"), close = document.getElementById("demo-close");
  var resting = null;
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
  };
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-demo]");
    if (!a) return;
    if (innerWidth > 760 && device) {
      e.preventDefault();
      resting = Array.prototype.slice.call(device.childNodes);
      device.replaceChildren(makeFrame(a));
    } else if (box && box.showModal) {
      e.preventDefault();
      inBox.textContent = "";
      inBox.appendChild(makeFrame(a));
      document.documentElement.style.overflow = "hidden";
      box.showModal();
    }
  });
  if (close) close.addEventListener("click", endDemo);
  if (box) box.addEventListener("close", endDemo);
  addEventListener("message", function (e) { if (e.origin === location.origin && e.data === "sj-demo-close") endDemo(); });
})();
