// Opens the demo in a dialog on the same page. No request is made until the player asks. Without <dialog> or JS, the links open it as a page.
(function () {
  var box = document.getElementById("demo-box"), frame = document.getElementById("demo-frame"), close = document.getElementById("demo-close");
  if (!box || !box.showModal) return;
  var shut = function () { frame.textContent = ""; if (box.open) box.close(); document.documentElement.style.overflow = ""; };
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-demo]");
    if (!a) return;
    e.preventDefault();
    var f = document.createElement("iframe");
    f.src = a.getAttribute("href"); f.title = box.getAttribute("aria-label"); f.allow = "autoplay";
    frame.textContent = ""; frame.appendChild(f);
    document.documentElement.style.overflow = "hidden";
    box.showModal();
  });
  close.addEventListener("click", shut);
  box.addEventListener("close", shut);
  window.addEventListener("message", function (e) { if (e.origin === location.origin && e.data === "sj-demo-close") shut(); });
})();
