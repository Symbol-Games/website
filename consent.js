/* Cookie consent (2026-11-18, the owner: Google Tag Manager on the site). Basic consent mode: nothing loads from Google until the
   visitor taps Accept; the choice is kept on this device; "Cookie settings" in the footer asks again. Refusing is as easy as accepting. */
(function () {
  var GTM = "GTM-WZJDBBPX", KEY = "si-consent", tr = (document.documentElement.lang || "tr").indexOf("tr") === 0;
  var T = tr ? { text: "Siteyi geliştirmek ve reklamlarımızı ölçmek için Google'ın çerezlerini kullanmak istiyoruz. İzin verirsen Google Tag Manager yüklenir.", yes: "Kabul et", no: "Reddet", more: "Gizlilik politikası", link: "Çerez tercihleri", url: "/gizlilik.html#site" }
             : { text: "We'd like to use Google's cookies to improve the site and measure our ads. If you agree, Google Tag Manager loads.", yes: "Accept", no: "Decline", more: "Privacy policy", link: "Cookie settings", url: "/en/privacy.html#site" };
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: "denied" });
  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  var loaded = false;
  function load() {
    if (loaded) return; loaded = true;
    gtag("consent", "update", { ad_storage: "granted", ad_user_data: "granted", ad_personalization: "granted", analytics_storage: "granted" });
    dataLayer.push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
    var s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtm.js?id=" + GTM; document.head.appendChild(s);
  }
  function banner() {
    if (document.getElementById("si-consent")) return;
    var b = document.createElement("div"); b.id = "si-consent"; b.setAttribute("role", "dialog"); b.setAttribute("aria-label", T.link);
    b.style.cssText = "position:fixed;left:12px;right:12px;bottom:12px;z-index:9999;max-width:560px;margin:0 auto;background:#111;color:#fff;border-radius:16px;padding:16px;box-shadow:0 8px 30px rgba(0,0,0,.35);font:15px/1.45 system-ui,sans-serif";
    b.innerHTML = '<p style="margin:0 0 12px">' + T.text + ' <a href="' + T.url + '" style="color:#F4B90B">' + T.more + '</a></p>' +
      '<div style="display:flex;gap:10px"><button data-v="no" style="flex:1;padding:11px;border-radius:12px;border:2px solid #F4B90B;background:#111;color:#F4B90B;font-weight:700;cursor:pointer">' + T.no + '</button>' +
      '<button data-v="yes" style="flex:1;padding:11px;border-radius:12px;border:2px solid #F4B90B;background:#F4B90B;color:#111;font-weight:700;cursor:pointer">' + T.yes + '</button></div>';
    b.addEventListener("click", function (e) { var v = e.target.getAttribute && e.target.getAttribute("data-v"); if (!v) return; save(v); b.remove(); if (v === "yes") load(); else if (loaded) location.reload(); });
    document.body.appendChild(b);
  }
  function footerLink() {
    var f = document.querySelector("footer"); if (!f || document.getElementById("si-consent-link")) return;
    var a = document.createElement("a"); a.id = "si-consent-link"; a.href = "#"; a.textContent = T.link; a.style.cssText = "display:inline-block;margin:8px 0;opacity:.8";
    a.addEventListener("click", function (e) { e.preventDefault(); banner(); }); f.appendChild(a);
  }
  var v = read(); if (v === "yes") load();
  document.addEventListener("DOMContentLoaded", function () { footerLink(); if (!v) banner(); });
})();
