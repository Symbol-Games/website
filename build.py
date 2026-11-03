"""Builds the Symbol Interactive site (symbolinteractive.com.tr) from the page texts below: python3 build.py

Turkish pages at the root, English under en/. One stylesheet; the fonts are the game's own (DynaPuff, Nunito), self-hosted (OFL).
"""
import math
import pathlib

ROOT = pathlib.Path(__file__).parent
MAIL = "destek@symbolinteractive.com.tr"
CONTROLLER = {"tr": "Cem Tezgelen", "en": "Cem Tezgelen"}  # the developer's own name, as the user gave it (2026-11-03)
UPDATED = {"tr": "3 Kasım 2026", "en": "3 November 2026"}


def star(cx, cy, r, fill, rot=0.0, inner=0.48):
    d = ""
    for i in range(10):
        a = -math.pi / 2 + rot + i * math.pi / 5
        k = r * inner if i % 2 else r
        d += ("L" if i else "M") + f"{cx + k * math.cos(a):.1f} {cy + k * math.sin(a):.1f}"
    return f'<path d="{d}Z" fill="{fill}" stroke="#fff" stroke-width="{r * 0.18:.1f}" stroke-linejoin="round"/>'


# The jar: the game's icon A, drawn large; its stars drop in once on load.
JAR_STARS = [(77, 193, 22, "#FF4FA6", .1), (123, 191, 22, "#14DCC8", -.25), (99, 156, 22, "#FFCC2E", .3), (75, 120, 19, "#A273FF", 0), (121, 118, 19, "#3FDD77", .2)]


def jar(size_class="hero-jar", animate=True):
    stars = "".join(f'<g class="drop" style="--i:{i}">{star(x, y, r, c, rot)}</g>' if animate else star(x, y, r, c, rot)
                    for i, (x, y, r, c, rot) in enumerate(JAR_STARS))
    return f'''<svg class="{size_class}" viewBox="0 0 200 240" role="img" aria-label="Yıldızlarla dolu cam kavanoz">
  <rect x="44" y="52" width="112" height="170" rx="40" fill="rgba(255,255,255,.13)" stroke="#fff" stroke-width="6"/>
  {stars}
  <rect x="58" y="70" width="8" height="34" rx="4" fill="#fff" opacity=".42"/>
  <rect x="62" y="30" width="76" height="28" rx="9" fill="#FFC93C" stroke="#fff" stroke-width="5"/>
</svg>'''


def page(lang, path, title, description, body, alt_href):
    prefix = "/" if path == "404.html" else "../" if lang == "en" else ""
    nav = {
        "tr": [("Destek", "destek.html"), ("Gizlilik", "gizlilik.html"), ("English", alt_href)],
        "en": [("Support", "support.html"), ("Privacy", "privacy.html"), ("Türkçe", alt_href)],
    }[lang]
    home = "index.html"
    hreflang = {"English": ' lang="en"', "Türkçe": ' lang="tr"'}
    links = "".join(f'<a href="{href}"{hreflang.get(text, "")}>{text}</a>' for text, href in nav)
    foot = {"tr": f'Bize yaz: <a href="mailto:{MAIL}">{MAIL}</a>', "en": f'Write to us: <a href="mailto:{MAIL}">{MAIL}</a>'}[lang]
    html = f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}site.css">
</head>
<body>
<header class="top">
  <a class="mark" href="{home}">Symbol Interactive</a>
  <nav>{links}</nav>
</header>
<main>
{body}
</main>
<footer class="bottom">
  <p>{foot}</p>
  <p>© 2026 Symbol Interactive</p>
</footer>
</body>
</html>
'''
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


HOME = {
    "tr": f'''<section class="hero">
  <div>
    <h1>Küçük, özenli mobil oyunlar</h1>
    <p class="lede">Symbol Interactive, telefonda birkaç dakikada açılıp uzun süre akılda kalan bulmaca oyunları yapan küçük bir stüdyo.</p>
  </div>
  {jar()}
</section>
<section class="game" aria-labelledby="game">
  {jar("icon-jar", animate=False)}
  <div>
    <h2 id="game">Yıldız Kavanozu</h2>
    <p>Renkli yıldızları kavanozlara ayırdığın sakin bir bulmaca. Her kavanoz mühürlendiğinde gökyüzünde bir takımyıldızın yıldızı yanar; seviyeler ilerledikçe gerçek takımyıldızları ve hikâyelerini tanırsın.</p>
    <p class="status">Yakında App Store ve Google Play'de. On üç dilde.</p>
  </div>
</section>''',
    "en": f'''<section class="hero">
  <div>
    <h1>Small, carefully made mobile games</h1>
    <p class="lede">Symbol Interactive is a small studio making puzzle games that open in a few minutes on your phone and stay with you much longer.</p>
  </div>
  {jar()}
</section>
<section class="game" aria-labelledby="game">
  {jar("icon-jar", animate=False)}
  <div>
    <h2 id="game">Star Jars</h2>
    <p>A calm puzzle where you sort colourful stars into jars. Every sealed jar lights a star of a constellation in the sky, and level by level you meet the real constellations and their stories.</p>
    <p class="status">Coming soon to the App Store and Google Play. In thirteen languages.</p>
  </div>
</section>''',
}

SUPPORT = {
    "tr": f'''<article class="prose">
<h1>Destek</h1>
<p>Bir sorun mu var, bir önerin mi? <a href="mailto:{MAIL}">{MAIL}</a> adresine yaz. Oyunun adını, telefonunun modelini ve ne olduğunu kısaca anlatırsan daha çabuk yardım edebiliriz.</p>
<h2>İlerlemem nerede saklanıyor?</h2>
<p>Telefonunda. Hesap açman gerekmez. Oyunu silersen ilerlemen de silinir.</p>
<h2>Satın aldığım bir şey görünmüyor</h2>
<p>Reklamları kaldırma gibi kalıcı satın almalar, oyunu aynı App Store ya da Google Play hesabıyla yeniden yüklediğinde geri gelir. Gelmezse bize yaz; satın alma tarihini ve mağazanın gönderdiği makbuzu eklemen yeterli.</p>
<h2>Para iadesi</h2>
<p>Ödemeleri mağazalar alır, iadeyi de onlar yapar: App Store için <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>, Google Play için <a href="https://support.google.com/googleplay/answer/2479637">Google Play iade sayfası</a>.</p>
<h2>Verilerimin silinmesini istiyorum</h2>
<p>Oyundaki ilerlemeni oyunu silerek kaldırabilirsin. Reklam ve analitik servislerinin tuttuğu verilerin silinmesi için bize yaz; ayrıntılar <a href="gizlilik.html">gizlilik politikasında</a>.</p>
</article>''',
    "en": f'''<article class="prose">
<h1>Support</h1>
<p>Something wrong, or an idea to share? Write to <a href="mailto:{MAIL}">{MAIL}</a>. Telling us the game, your phone model and what happened helps us help you sooner.</p>
<h2>Where is my progress saved?</h2>
<p>On your phone. You don't need an account. If you delete the game, your progress goes with it.</p>
<h2>Something I bought is missing</h2>
<p>Permanent purchases, such as removing ads, come back when you install the game again with the same App Store or Google Play account. If one doesn't, write to us with the purchase date and the receipt the store sent you.</p>
<h2>Refunds</h2>
<p>The stores take the payments and handle refunds: <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a> for the App Store, and <a href="https://support.google.com/googleplay/answer/2479637">Google Play's refund page</a> for Google Play.</p>
<h2>Deleting my data</h2>
<p>Deleting the game removes your progress. To have data held by the ad and analytics services deleted, write to us; the details are in the <a href="privacy.html">privacy policy</a>.</p>
</article>''',
}

PRIVACY = {
    "tr": f'''<article class="prose">
<h1>Gizlilik politikası</h1>
<p class="meta">Son güncelleme: {UPDATED["tr"]}</p>
<p>Bu politika, Symbol Interactive'in mobil oyunlarının (Yıldız Kavanozu ve sonrakiler) hangi bilgileri neden işlediğini anlatır. Veri sorumlusu: {CONTROLLER["tr"]}. Her soru için: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
<h2>Kısaca</h2>
<ul>
<li>Oyun için hesap açman gerekmez; adını, e-postanı ya da telefon numaranı istemeyiz.</li>
<li>İlerlemen telefonunda saklanır.</li>
<li>Satın almaları Apple ve Google yönetir; kart bilgilerini hiç görmeyiz.</li>
<li>Reklamlar ve analitik için bazı cihaz bilgileri, aşağıda adı geçen servislerce işlenir. Kişiselleştirilmiş reklam yalnızca iznin varsa gösterilir.</li>
</ul>
<h2>Hangi bilgiler, neden</h2>
<p><strong>Oyun ilerlemesi.</strong> Seviyeler, yıldızlar, ayarlar ve satın aldığın öğeler telefonunda saklanır. Oyunu silersen bunlar da silinir.</p>
<p><strong>Satın almalar.</strong> Ödeme App Store ya da Google Play üzerinden yapılır. Biz yalnızca satın alma kaydını (hangi ürün, işlem numarası) alır ve öğeyi vermek için kullanırız.</p>
<p><strong>Reklamlar.</strong> Oyundaki reklamları Unity LevelPlay ve onun çalıştığı reklam ağları gösterir. Bu servisler reklamı göstermek, ölçmek ve dolandırıcılığı önlemek için şunları işleyebilir: reklam kimliği (iOS'ta IDFA, Android'de reklam kimliği), IP adresi ve buna dayalı yaklaşık konum, cihaz modeli, işletim sistemi ve dil, reklamla etkileşimin. iOS'ta reklam kimliği yalnızca uygulama takibine izin verirsen kullanılır. Kişiselleştirilmiş reklamlar için izin isteriz; izin vermezsen kişiselleştirilmemiş reklamlar görürsün. Reklamları kaldıran satın almadan sonra reklam gösterilmez.</p>
<p><strong>Analitik ve çökme raporları.</strong> Oyunu geliştirmek için Google Firebase Analytics ve Crashlytics kullanırız: hangi seviyelerin oynandığı, oturum süresi, cihaz modeli ve çökme kayıtları. Bu bilgiler adınla ya da e-postanla eşleştirilmez.</p>
<p><strong>Destek yazışmaları.</strong> Bize e-posta yazarsan, adresini ve mesajını yalnızca cevap vermek için saklarız.</p>
<h2>Paylaşım ve yurt dışına aktarım</h2>
<p>Bilgileri satmayız. Yukarıdaki servis sağlayıcılar (Apple, Google, Unity ve reklam ortakları) bilgileri kendi sunucularında, Türkiye dışında da işleyebilir. Bu aktarım, izin gereken durumlarda iznine dayanır. Her servisin kendi gizlilik politikası vardır: <a href="https://www.apple.com/legal/privacy/">Apple</a>, <a href="https://policies.google.com/privacy">Google</a>, <a href="https://unity.com/legal/privacy-policy">Unity</a>.</p>
<h2>Çocuklar</h2>
<p>Oyunlarımız 13 yaşın altındaki çocuklara yönelik değildir ve bu yaştakilerden bilerek bilgi toplamayız.</p>
<h2>Saklama süresi</h2>
<p>Destek yazışmaları, iş bitince en geç bir yıl içinde silinir. Analitik verileri en fazla 14 ay saklanır.</p>
<h2>Hakların</h2>
<p>KVKK'nın 11. maddesi ve (Avrupa'daysan) GDPR kapsamında bilgilerinin işlenip işlenmediğini öğrenme, düzeltilmesini ya da silinmesini isteme, işlemeye itiraz etme ve verdiğin izni geri alma hakların var. Bunun için <a href="mailto:{MAIL}">{MAIL}</a> adresine yaz; en geç 30 gün içinde cevap veririz. İznini telefonundan da geri alabilirsin: iOS'ta takip iznini Ayarlar'dan, Android'de reklam kimliğini telefon ayarlarından.</p>
<h2>Değişiklikler</h2>
<p>Bu politikayı değiştirirsek güncel hâlini bu sayfada, yeni tarihiyle yayınlarız.</p>
</article>''',
    "en": f'''<article class="prose">
<h1>Privacy policy</h1>
<p class="meta">Last updated: {UPDATED["en"]}</p>
<p>This policy explains what information Symbol Interactive's mobile games (Star Jars and those to come) process and why. Data controller: {CONTROLLER["en"]}. For any question: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
<h2>In short</h2>
<ul>
<li>You don't need an account to play; we never ask for your name, email or phone number.</li>
<li>Your progress is saved on your phone.</li>
<li>Apple and Google handle purchases; we never see your card details.</li>
<li>For ads and analytics, some device information is processed by the services named below. Personalised ads are shown only with your consent.</li>
</ul>
<h2>What information, and why</h2>
<p><strong>Game progress.</strong> Levels, stars, settings and the items you bought are stored on your phone. Deleting the game deletes them too.</p>
<p><strong>Purchases.</strong> Payments go through the App Store or Google Play. We receive only the purchase record (which product, the transaction number) and use it to give you the item.</p>
<p><strong>Ads.</strong> The ads in our games are served by Unity LevelPlay and the ad networks it works with. To show and measure ads and to prevent fraud, these services may process your advertising ID (IDFA on iOS, the advertising ID on Android), your IP address and the approximate location it suggests, your device model, operating system and language, and how you interact with ads. On iOS the advertising ID is used only if you allow app tracking. We ask for your consent to personalised ads; without it you see non-personalised ads. After the purchase that removes ads, no ads are shown.</p>
<p><strong>Analytics and crash reports.</strong> To improve our games we use Google Firebase Analytics and Crashlytics: which levels are played, session length, device model and crash logs. This information is not matched to your name or email.</p>
<p><strong>Support emails.</strong> If you write to us, we keep your address and message only to answer you.</p>
<h2>Sharing and transfers abroad</h2>
<p>We don't sell information. The service providers above (Apple, Google, Unity and ad partners) may process it on their own servers, including outside Türkiye. Where consent is required, these transfers rely on it. Each service has its own privacy policy: <a href="https://www.apple.com/legal/privacy/">Apple</a>, <a href="https://policies.google.com/privacy">Google</a>, <a href="https://unity.com/legal/privacy-policy">Unity</a>.</p>
<h2>Children</h2>
<p>Our games are not directed at children under 13, and we do not knowingly collect information from them.</p>
<h2>How long we keep it</h2>
<p>Support emails are deleted within a year of the matter being closed. Analytics data is kept for at most 14 months.</p>
<h2>Your rights</h2>
<p>Under Article 11 of Türkiye's KVKK and, if you are in Europe, the GDPR, you can ask whether your information is processed, have it corrected or deleted, object to its processing and withdraw your consent. Write to <a href="mailto:{MAIL}">{MAIL}</a>; we answer within 30 days. You can also withdraw consent on your phone: app tracking in iOS Settings, the advertising ID in Android's settings.</p>
<h2>Changes</h2>
<p>If we change this policy, we publish the new version on this page with its new date.</p>
</article>''',
}

NOT_FOUND = '''<article class="prose">
<h1>Bu sayfa yok</h1>
<p>Adres yanlış yazılmış ya da sayfa taşınmış olabilir. <a href="/">Ana sayfaya dön</a>.</p>
<p lang="en">This page doesn't exist. <a href="/en/">Go to the home page</a>.</p>
</article>'''

page("tr", "index.html", "Symbol Interactive", "Küçük, özenli mobil oyunlar: Yıldız Kavanozu.", HOME["tr"], "en/index.html")
page("en", "en/index.html", "Symbol Interactive", "Small, carefully made mobile games: Star Jars.", HOME["en"], "../index.html")
page("tr", "destek.html", "Destek · Symbol Interactive", "Symbol Interactive oyunları için destek.", SUPPORT["tr"], "en/support.html")
page("en", "en/support.html", "Support · Symbol Interactive", "Support for Symbol Interactive games.", SUPPORT["en"], "../destek.html")
page("tr", "gizlilik.html", "Gizlilik politikası · Symbol Interactive", "Symbol Interactive oyunlarının gizlilik politikası.", PRIVACY["tr"], "en/privacy.html")
page("en", "en/privacy.html", "Privacy policy · Symbol Interactive", "Privacy policy of Symbol Interactive games.", PRIVACY["en"], "../gizlilik.html")
page("tr", "404.html", "Sayfa yok · Symbol Interactive", "Sayfa bulunamadı.", NOT_FOUND, "/en/")
(ROOT / "favicon.svg").write_text(jar("fav", animate=False).replace('class="fav" ', 'xmlns="http://www.w3.org/2000/svg" '), encoding="utf-8")
(ROOT / "CNAME").write_text("symbolinteractive.com.tr\n", encoding="utf-8")
app_ads = ROOT / "app-ads.txt"
if not app_ads.exists():  # the ad networks' lines come with the real ads (LevelPlay); never overwritten here
    app_ads.write_text("# Symbol Interactive: authorized sellers of our apps' ad inventory (IAB app-ads.txt). Lines are added with the ad networks.\n", encoding="utf-8")
print("built")
