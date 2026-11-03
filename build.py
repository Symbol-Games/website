"""Builds the Symbol Interactive site (symbolinteractive.com.tr) from the page texts below: python3 build.py

Turkish pages at the root, English under en/. One stylesheet; the fonts are the game's own (DynaPuff, Nunito), self-hosted (OFL).
"""
import math
import pathlib

ROOT = pathlib.Path(__file__).parent
MAIL = "symbolinteractive@gmail.com"  # the support address the user set in the release checklist (2026-11-03)
CONTROLLER = {"tr": "Cem Tezgelen", "en": "Cem Tezgelen"}  # the developer's own name, as the user gave it (2026-11-03)
UPDATED = {"tr": "4 Kasım 2026", "en": "4 November 2026"}  # the store-version draft's date; set to the store release day when it goes live


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
    prefix = "/" if path == "404.html" else "../" if "/" in path else ""
    nav = {
        "tr": [("Destek", prefix + "destek.html" if prefix != "../" else "destek.html"), ("Gizlilik", "gizlilik.html"), ("English", alt_href)],
        "en": [("Support", "support.html"), ("Privacy", "privacy.html"), ("Türkçe", alt_href)],
    }[lang]
    if lang == "en" and "/" not in path:  # an English page at the root (the App Store's /support and /starjars)
        nav = [("Support", "en/support.html"), ("Privacy", "en/privacy.html"), ("Türkçe", alt_href)]
    home = "index.html"
    hreflang = {"English": ' lang="en"', "Türkçe": ' lang="tr"'}
    links = "".join(f'<a href="{href}"{hreflang.get(text, "")}>{text}</a>' for text, href in nav)
    # The account-deletion page (Google Play's Data safety form asks for its URL) is linked from every footer.
    delete_href = prefix + "hesap-silme.html" if lang == "tr" else "delete-account.html" if "/" in path else "en/delete-account.html"
    foot = {"tr": f'Bize yaz: <a href="mailto:{MAIL}">{MAIL}</a> · <a href="{delete_href}">Hesap silme</a>',
            "en": f'Write to us: <a href="mailto:{MAIL}">{MAIL}</a> · <a href="{delete_href}">Delete account</a>'}[lang]
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
<p>Telefonunda ve bulut kaydında. Oyun ilk açılışta senin için anonim bir hesap açar ve ilerlemeni ona kaydeder. Ayarlar → Bulut kaydı'ndan Apple ya da Google hesabını bağlarsan ilerlemen yeni telefonuna da gelir.</p>
<h2>Satın aldığım bir şey görünmüyor</h2>
<p>Reklamları kaldırma gibi kalıcı satın almalar, oyunu aynı App Store ya da Google Play hesabıyla yeniden yüklediğinde geri gelir. Gelmezse bize yaz; satın alma tarihini ve mağazanın gönderdiği makbuzu eklemen yeterli.</p>
<h2>Para iadesi</h2>
<p>Ödemeleri mağazalar alır, iadeyi de onlar yapar: App Store için <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>, Google Play için <a href="https://support.google.com/googleplay/answer/2479637">Google Play iade sayfası</a>.</p>
<h2>Verilerimin silinmesini istiyorum</h2>
<p>Hesabını ve bulut kaydını oyunun içinden silebilirsin: Ayarlar → Bulut kaydı → Hesabı sil. Oyunu açamıyorsan bize yaz. Neyin silinip neyin kaldığı <a href="hesap-silme.html">hesap silme sayfasında</a>, diğer veriler <a href="gizlilik.html">gizlilik politikasında</a>.</p>
</article>''',
    "en": f'''<article class="prose">
<h1>Support</h1>
<p>Something wrong, or an idea to share? Write to <a href="mailto:{MAIL}">{MAIL}</a>. Telling us the game, your phone model and what happened helps us help you sooner.</p>
<h2>Where is my progress saved?</h2>
<p>On your phone and in your cloud save. On first launch the game creates an anonymous account for you and saves your progress to it. Link your Apple or Google account in Settings → Cloud save, and your progress comes with you to a new phone.</p>
<h2>Something I bought is missing</h2>
<p>Permanent purchases, such as removing ads, come back when you install the game again with the same App Store or Google Play account. If one doesn't, write to us with the purchase date and the receipt the store sent you.</p>
<h2>Refunds</h2>
<p>The stores take the payments and handle refunds: <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a> for the App Store, and <a href="https://support.google.com/googleplay/answer/2479637">Google Play's refund page</a> for Google Play.</p>
<h2>Deleting my data</h2>
<p>You can delete your account and cloud save in the game: Settings → Cloud save → Delete account. If you can't open the game, write to us. What is deleted and what remains is on the <a href="delete-account.html">account deletion page</a>; everything else is in the <a href="privacy.html">privacy policy</a>.</p>
</article>''',
}

# The store version (1.0.0) of Star Jars: Firebase (Analytics, Crashlytics, Remote Config, Authentication, Firestore), LevelPlay ads,
# store purchases. From the spec 2026-11-03-star-jars-store-version-design.md §3, §3.1, §3.5, §3.6.
# Points a lawyer should settle are marked <!-- REVIEW: ... --> in the text; build.py counts them, and none may go live.
PRIVACY = {
    "tr": f'''<article class="prose">
<h1>Gizlilik politikası</h1>
<p class="meta">Son güncelleme: {UPDATED["tr"]}</p>
<p>Bu politika, Symbol Interactive'in mobil oyunu Yıldız Kavanozu'nun (mağazalarda Star Jars Sort Deluxe) hangi bilgileri neden işlediğini, kimlerin aldığını, ne kadar saklandığını ve haklarını anlatır. Yeni bir oyun çıkardığımızda onun bilgilerini de bu sayfaya ekleriz.</p>
<p><strong>Veri sorumlusu:</strong> {CONTROLLER["tr"]}, Symbol Interactive adıyla oyun yapan bireysel geliştirici, Türkiye. Her soru ve istek için: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
<!-- REVIEW: GDPR Art. 27 (and UK GDPR Art. 27): a controller outside the EU/UK that offers the game to players there may have to name a representative in the EU and in the UK, unless the processing is occasional and low-risk. If one is needed, add the representative's name and contact here. -->
<h2>Kısaca</h2>
<ul>
<li>Oyun ilk açılışta senin için anonim bir hesap açar; adını, e-postanı ya da telefon numaranı istemeyiz. Apple ya da Google hesabını bağlamak isteğe bağlıdır.</li>
<li>İlerlemen telefonunda ve bulut kaydı olarak Google'ın Avrupa'daki (Belçika) sunucularında saklanır.</li>
<li>Satın almaları Apple ve Google yönetir; kart bilgilerini hiç görmeyiz.</li>
<li>Reklamlar, analitik ve çökme raporları için bazı cihaz bilgileri, aşağıda adı geçen servislerce işlenir. Rıza gereken ülkelerde kişiselleştirilmiş reklam yalnızca iznin varsa gösterilir.</li>
<li>Hesabını ve bulut kaydını istediğin an oyunun içinden silebilirsin: Ayarlar → Bulut kaydı → Hesabı sil.</li>
</ul>
<h2>Hangi bilgiler, neden</h2>
<p><strong>Hesap.</strong> Oyun ilk açıldığında Google Firebase Authentication senin için anonim bir hesap açar. Bu hesabın yalnızca rastgele bir kimlik numarası vardır; oyunun ayarlarında oyuncu kimliğin olarak görünür. İstersen hesabını Ayarlar'dan Apple ile Giriş'e ya da Google hesabına bağlayabilirsin; o zaman Firebase, Apple'ın ya da Google'ın verdiği hesap kimliğini ve paylaşmayı seçtiğin bilgileri (örneğin e-posta adresin; Apple'da adresini gizleyebilirsin) alır. Bunları yalnızca seni tanımak ve ilerlemeni başka bir telefona taşımak için kullanırız. Firebase Authentication, hesapları kötüye kullanıma karşı korumak için IP adreslerini birkaç hafta kayıtlı tutar.</p>
<!-- REVIEW: what the linked account record holds depends on the scopes the game requests when linking (Sign in with Apple: email/name; Google: email/profile; Play Games: player ID). If no email or name is requested, remove the "örneğin e-posta adresin" clause here and in English, and keep the store forms in step. -->
<p><strong>Bulut kaydı.</strong> İlerlemeni kaybetmemen ve yeni bir telefona taşıyabilmen için kaydın, hesabına bağlı olarak Google Cloud Firestore'da, Avrupa Birliği'ndeki europe-west1 bölgesinde (Belçika) saklanır. Kayıtta oyun ilerlemen (seviyeler, yıldızlar, yıldız tozu ve öğelerin), ayarların, bir ilerleme özeti (seviye, yıldız ve toz sayısı), cihazının modeli ve kaydın zamanları bulunur. Bu kaydı yalnızca senin hesabın okuyup yazabilir. İlerlemenin bir kopyası telefonunda da durur.</p>
<p><strong>Satın almalar.</strong> Ödemeyi App Store ya da Google Play alır; kart bilgilerini hiç görmeyiz. Mağazadan yalnızca satın alma makbuzunu (hangi ürün, işlem numarası, zaman) alır, öğeyi vermek ve gerektiğinde geri yüklemek için kullanırız. Satın almanın tutarı ve para birimi, gelir raporlarımız için Firebase Analytics'e de gider.</p>
<p><strong>Reklamlar.</strong> Oyun, Unity LevelPlay aracılığıyla ironSource Ads, Unity Ads ve Google AdMob reklamları gösterir: bir ödül için izlemeyi kendin seçtiğin ödüllü reklamlar ve bazı galibiyetlerden sonra iki seviye arasında çıkan geçiş reklamları. Banner reklam yoktur. Bu servisler reklamları seçmek, göstermek, ölçmek ve dolandırıcılığı önlemek için şunları işler: reklam kimliğin (Android'de reklam kimliği; iOS'ta IDFA, yalnızca oyunun sorduğu uygulama takibi sorusuna izin verirsen), IP adresin ve ona dayanan yaklaşık konumun, cihaz bilgilerin (model, işletim sistemi, dil gibi) ve reklamlarla etkileşimin. Kişiselleştirilmiş reklamda reklam ortakları, ilgi alanlarını tahmin etmek için bu bilgileri başka uygulama ve sitelerden gelen bilgilerle birleştirebilir. Avrupa Ekonomik Alanı'nda, Birleşik Krallık'ta ve İsviçre'de oyun, Google'ın rıza mesajıyla iznini sorar; izin vermezsen reklamlar ilgi alanlarına göre seçilmez. ABD'nin gizlilik yasası olan eyaletlerinde de bilgilerinin kişiselleştirilmiş reklam için kullanılmasını reddedebilirsin. Reklamsız satın alımı geçiş reklamlarını kapatır; ödüllü reklamlar, istediğinde izleyebilmen için kalır. Reklam gösterimlerinin gelirini (reklam ağı, reklam türü, tutar) Firebase Analytics'te ölçeriz.</p>
<p><strong>Analitik.</strong> Oyunu geliştirmek ve zorluğunu dengelemek için Google Firebase Analytics kullanırız. Analytics; oyundaki etkileşimlerini (açılan ekranlar, başlanan, kazanılan ve kaybedilen seviyeler, oturum süresi, satın almalar, izlenen reklamlar), cihaz ve uygulama bilgilerini (model, işletim sistemi, uygulama sürümü, dil), oyunun bu telefondaki kopyasına özgü bir kimliği ve IP adresinden çıkarılan yaklaşık konumu (ülke ve şehir düzeyinde) işler. Avrupa Ekonomik Alanı'nda, Birleşik Krallık'ta ve İsviçre'de Analytics, Google'ın rıza modunda çalışır ve rıza mesajında yaptığın seçime uyar. Bu bilgiler adınla ya da e-postanla eşleştirilmez.</p>
<!-- REVIEW: Firebase Analytics also collects the advertising ID when it is available (the Android build declares AD_ID; on iOS after ATT permission). Either turn that off (google_analytics_adid_collection_enabled = false on both platforms) or name the advertising ID here and in the store forms. And if the game passes the Firebase uid to Analytics (SetUserId) or to LevelPlay as the user ID, the analytics/ad data becomes linked to the account: then the "not matched" sentence and both deletion pages must change, and a deletion would also need Google Analytics' user deletion API. -->
<p><strong>Çökme raporları.</strong> Hataları bulup düzeltmek için Firebase Crashlytics kullanırız. Oyun çöktüğünde ya da bir hata kaydettiğinde Crashlytics; hata kaydını, teşhis bilgilerini (cihaz modeli, işletim sistemi ve uygulama sürümü, bellek durumu, zaman) ve rastgele bir kurulum kimliğini alır.</p>
<p><strong>Uzaktan ayarlar.</strong> Firebase Remote Config ile oyunun bazı ayarlarını (örneğin reklam sıklığını) güncelleme yayınlamadan değiştiririz. Bunun için Firebase, oyunun bu kurulumuna özgü bir kimlik (Firebase kurulum kimliği) kullanır.</p>
<p><strong>Destek yazışmaları.</strong> Bize e-posta yazarsan, adresini ve mesajını yalnızca cevap vermek ve isteğini yerine getirmek için kullanırız.</p>
<h2>Hangi hukuki sebeple</h2>
<ul>
<li><strong>Sözleşmenin kurulması ve ifası</strong> (KVKK m. 5/2-c, GDPR m. 6/1-b): hesap, bulut kaydı, satın almalar ve destek. Bunlar, oyunda kullandığın hizmetin parçasıdır.</li>
<li><strong>Meşru menfaat</strong> (KVKK m. 5/2-f, GDPR m. 6/1-f): çökme raporları, uzaktan ayarlar, reklamların gösterilmesi ve ölçülmesi, dolandırıcılığın önlenmesi; rıza mesajı gösterilmeyen ülkelerde ayrıca analitik ve reklamların kişiselleştirilmesi. Oyunu çalışır, dengeli ve ücretsiz tutmak meşru menfaatimizdir. Bu işlemeye itiraz edebilirsin; reklamların kişiselleştirilmesini telefonunun reklam ayarlarından kapatabilirsin.</li>
<li><strong>Rıza</strong> (KVKK m. 5/1'deki açık rıza, GDPR m. 6/1-a): Avrupa Ekonomik Alanı'nda, Birleşik Krallık'ta ve İsviçre'de kişiselleştirilmiş reklam ve analitik; her ülkede iOS'ta uygulama takibi. Rızanı istediğin an geri alabilirsin.</li>
</ul>
<!-- REVIEW: Türkiye and KVKK. The consent message (Google UMP) is shown only in the EEA, the UK, Switzerland and US states, so in Türkiye analytics and personalised ads run without a prompt (on Android the advertising ID is available unless the player turns it off). The KVKK Authority's guidance on cookies treats analytics and advertising tracking as generally needing explicit consent (açık rıza), and KVKK Art. 5/2-f may not carry it. Ask a lawyer whether Türkiye needs its own consent prompt; if so, the "rıza mesajı gösterilmeyen ülkelerde" clause above must change (and the game with it). -->
<!-- REVIEW: legitimate interest for Crashlytics, Remote Config and non-personalised ads in the EEA/UK: the ePrivacy rules can require consent to store or read identifiers on the device unless strictly necessary. Confirm the basis for each purpose. -->
<h2>Kimler alır</h2>
<p>Bilgilerini kimseye para karşılığında satmayız. Yukarıdaki işler için bilgiler aşağıdaki şirketlere gider; her birinin kendi gizlilik politikası vardır.</p>
<ul>
<li><strong>Google:</strong> Firebase (Analytics, Crashlytics, Remote Config, Authentication, Cloud Firestore), AdMob ve Google Play. <a href="https://policies.google.com/privacy">Google Gizlilik Politikası</a>, <a href="https://firebase.google.com/support/privacy">Firebase'de gizlilik</a>, <a href="https://policies.google.com/technologies/partner-sites">Google'ın, hizmetlerini kullanan uygulamalardan gelen bilgileri nasıl kullandığı</a>.</li>
<li><strong>Unity:</strong> LevelPlay, Unity Ads ve ironSource Ads (ironSource, Unity'nin bir şirketidir). <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity'nin oyuncu ve uygulama kullanıcısı gizlilik politikası</a>.</li>
<li><strong>Apple:</strong> App Store ve Apple ile Giriş. <a href="https://www.apple.com/legal/privacy/">Apple Gizlilik Politikası</a>.</li>
</ul>
<p>Firebase'de Google, bilgileri bizim adımıza işler. Reklam ağları ve mağazalar ise bilgileri kendi politikalarına göre kendi amaçları için de kullanabilir. ABD'nin bazı eyalet yasaları, reklam ortaklarının kişiselleştirilmiş reklam için bilgi almasını "satış" ya da "paylaşım" sayar; bu eyaletlerde bunu oyundaki Gizlilik seçenekleri satırından reddedebilirsin. Bir yasa gerektirirse bilgileri yetkili makamlarla da paylaşırız.</p>
<!-- REVIEW: roles. Firebase services are processed by Google on our behalf under the Firebase Data Processing and Security Terms, but Google Analytics has its own terms and data-sharing settings (Google may act as a controller for some uses); AdMob and Unity's ad networks act as independent controllers for ads. Confirm each role and that the Analytics data-sharing settings match "bizim adımıza". US state laws (CCPA/CPRA and others) have thresholds: confirm whether they apply and whether the "satış/paylaşım" sentence is needed. Unity's player policy covers Unity Ads and LevelPlay and names ironSource as an affiliate (the old ironSource Mobile policy URL now redirects to unity.com/legal); confirm there is no separate ironSource Ads end-user policy to link. -->
<h2>Yurt dışına aktarım</h2>
<p>Bulut kaydın Avrupa Birliği'nde (Belçika) saklanır. Google, Unity ve Apple bilgileri Türkiye ve Avrupa Birliği dışında, örneğin Amerika Birleşik Devletleri'nde de işler. Bu aktarımlar, bu şirketlerin standart sözleşme hükümlerine dayanır.</p>
<!-- REVIEW: KVKK Art. 9 (as amended by Law No. 7499, in force since 1 June 2024): a transfer abroad on "appropriate safeguards" uses the KVKK Board's own standard contract, which the data controller must notify to the Authority within five business days of signing; the providers' EU standard contractual clauses may not meet that by themselves. Confirm the KVKK basis for each provider (Google, Unity, Apple). For EEA players, confirm whether each provider relies on the EU SCCs or the EU-US Data Privacy Framework. -->
<h2>Saklama süresi</h2>
<ul>
<li><strong>Hesap ve bulut kaydı:</strong> sen silene kadar. Oyun bir hesapla 24 ay boyunca hiç açılmazsa, o hesabı ve bulut kaydını biz sileriz.</li>
<li><strong>Analitik:</strong> Analytics olay verileri, Google'daki saklama ayarımızla 14 ay sonra silinir. Bunlardan üretilen, kimseyi tanıtmayan toplu sayılar (örneğin günlük oyuncu sayısı) daha uzun kalabilir.</li>
<li><strong>Çökme raporları:</strong> Google'ın belirlediği süreyle; Crashlytics çökme kayıtlarını ve bağlı kimlikleri 90 gün saklar.</li>
<li><strong>Reklam ortakları:</strong> kendi politikalarındaki sürelerle (bağlantılar yukarıda).</li>
<li><strong>Satın almalar:</strong> aldığın öğeler ilerlemenin parçası olarak yukarıdaki gibi saklanır. Apple ve Google kendi satın alma kayıtlarını kendi politikalarına göre tutar.</li>
<li><strong>Destek yazışmaları:</strong> iş bittikten sonra en geç bir yıl içinde silinir.</li>
</ul>
<h2>Hakların</h2>
<p>6698 sayılı Kişisel Verilerin Korunması Kanunu'nun (KVKK) 11. maddesine göre şu hakların var: kişisel verilerinin işlenip işlenmediğini öğrenme, işlendiyse bilgi isteme, işleme amacını ve amaca uygun kullanılıp kullanılmadığını öğrenme, yurt içinde ya da yurt dışında kimlere aktarıldığını bilme, eksik ya da yanlışsa düzeltilmesini, kanundaki şartlar varsa silinmesini ya da yok edilmesini ve bunların aktarıldığı kişilere bildirilmesini isteme, yalnızca otomatik sistemlerle yapılan bir analizin aleyhine bir sonuç doğurmasına itiraz etme ve kanuna aykırı işleme yüzünden zarara uğradıysan zararının giderilmesini isteme.</p>
<p>Avrupa Ekonomik Alanı'nda, Birleşik Krallık'ta ya da İsviçre'deysen GDPR ve benzeri yasalara göre de bilgilerine erişme, düzeltilmesini ya da silinmesini isteme, işlemenin kısıtlanmasını isteme, bilgilerini taşınabilir bir biçimde alma, meşru menfaate dayanan işlemeye itiraz etme ve verdiğin rızayı geri alma hakların var.</p>
<p>Bir hakkını kullanmak için <a href="mailto:{MAIL}">{MAIL}</a> adresine yaz ve oyunun ayarlarında görünen oyuncu kimliğini ekle; bilgilerini bu kimlikle buluruz. En geç 30 gün içinde, ücretsiz cevap veririz. Cevabımızdan memnun kalmazsan Türkiye'de Kişisel Verileri Koruma Kurulu'na, Avrupa'da yaşadığın ülkenin veri koruma otoritesine şikâyette bulunabilirsin.</p>
<!-- REVIEW: KVKK's Communiqué on the procedures for applications to the data controller lists the accepted channels (written application, KEP, secure electronic or mobile signature, an email address the applicant has already given the controller and that is registered in its system, or an application/software built for the purpose). Players here have anonymous accounts, so a plain email may not strictly qualify; confirm that email plus the player ID (and the in-game deletion) is acceptable, or list another channel. -->
<h2>Rızanı geri almak</h2>
<p>Rıza mesajının gösterildiği yerlerde (Avrupa Ekonomik Alanı, Birleşik Krallık, İsviçre ve ABD'nin bazı eyaletleri) oyunun Ayarlar ekranında <strong>Gizlilik seçenekleri</strong> satırı görünür; seçimini oradan istediğin an değiştirebilirsin. Her ülkede telefonunun ayarlarını da kullanabilirsin: iOS'ta Ayarlar → Gizlilik ve Güvenlik → Takip'ten oyunun takip iznini kapatabilir, Android'de telefon ayarlarının reklamlar bölümünden reklam kimliğini silebilir ya da sıfırlayabilirsin. Rızanı geri alman, o ana kadar yapılan işlemeyi etkilemez.</p>
<h2>Hesabını silmek</h2>
<p>Hesabını ve bulut kaydını oyunun içinden silebilirsin: <strong>Ayarlar → Bulut kaydı → Hesabı sil</strong>. Oyunu açamıyorsan bize e-postayla yazabilirsin. Neyin silinip neyin kaldığı ve ne kadar sürdüğü <a href="hesap-silme.html">hesap silme sayfasında</a>.</p>
<h2>Çocuklar</h2>
<p>Oyunlarımız 13 yaşın altındaki çocuklara yönelik değildir ve bu yaştakilerden bilerek bilgi toplamayız. 13 yaşından küçük bir çocuğun bilgilerinin bize ulaştığını düşünüyorsan bize yaz; bilgileri sileriz.</p>
<!-- REVIEW: GDPR Art. 8 sets the age of digital consent between 13 and 16 depending on the country (16 in e.g. Germany, the Netherlands, Ireland). With a 13+ audience, a 13-15-year-old there cannot consent alone to personalised ads or analytics; check whether the UMP setup needs the "under the age of consent" handling, or whether the audience or this text must change. Check the same for minors' explicit consent under Turkish law. -->
<h2>Değişiklikler</h2>
<p>Bu politikayı değiştirirsek güncel hâlini bu sayfada, yeni tarihiyle yayınlarız.</p>
</article>''',
    "en": f'''<article class="prose">
<h1>Privacy policy</h1>
<p class="meta">Last updated: {UPDATED["en"]}</p>
<p>This policy explains what information Symbol Interactive's mobile game Star Jars Sort Deluxe (Yıldız Kavanozu in Turkish) processes and why, who receives it, how long it is kept, and what your rights are. When we release a new game, we add its details to this page.</p>
<p><strong>Data controller:</strong> {CONTROLLER["en"]}, an individual developer making games as Symbol Interactive, Türkiye. For any question or request: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
<!-- REVIEW: GDPR Art. 27 (and UK GDPR Art. 27): see the Turkish page; add an EU/UK representative here if one is needed. -->
<h2>In short</h2>
<ul>
<li>On first launch the game creates an anonymous account for you; we never ask for your name, email or phone number. Linking an Apple or Google account is optional.</li>
<li>Your progress is saved on your phone and, as a cloud save, on Google's servers in Europe (Belgium).</li>
<li>Apple and Google handle purchases; we never see your card details.</li>
<li>For ads, analytics and crash reports, some device information is processed by the services named below. Where consent is required, personalised ads are shown only with your consent.</li>
<li>You can delete your account and cloud save in the game at any time: Settings → Cloud save → Delete account.</li>
</ul>
<h2>What information, and why</h2>
<p><strong>Account.</strong> When the game first opens, Google Firebase Authentication creates an anonymous account for you. All it has is a random ID, shown in the game's settings as your player ID. If you like, you can link the account to Sign in with Apple or to your Google account in Settings; Firebase then receives the account ID that Apple or Google gives it and the details you choose to share (such as your email address; Apple lets you hide yours). We use these only to recognise you and to bring your progress to another phone. Firebase Authentication keeps a log of IP addresses for a few weeks to protect accounts from abuse.</p>
<!-- REVIEW: linked-account scopes: see the Turkish page; drop "such as your email address" if no email is requested. -->
<p><strong>Cloud save.</strong> So that you don't lose your progress and can take it to a new phone, your save is stored with your account in Google Cloud Firestore, in the europe-west1 region (Belgium, in the European Union). It holds your game progress (levels, stars, stardust and your items), your settings, a progress summary (level, stars and stardust), your device model and when it was saved. Only your own account can read or write it. A copy of your progress also stays on your phone.</p>
<p><strong>Purchases.</strong> The App Store or Google Play takes the payment; we never see your card details. From the store we receive only the purchase receipt (which product, the transaction ID, the time), and we use it to give you the item and to restore it when needed. The amount and currency of a purchase also go to Firebase Analytics for our revenue reports.</p>
<p><strong>Ads.</strong> The game shows ads from ironSource Ads, Unity Ads and Google AdMob through Unity LevelPlay: rewarded ads, which you choose to watch for a reward, and interstitial ads, which appear between levels after some wins. There are no banner ads. To choose, show and measure ads and to prevent fraud, these services process your advertising ID (on Android the advertising ID; on iOS the IDFA, only if you allow tracking when the game asks), your IP address and the approximate location it suggests, device information (such as model, operating system and language) and how you interact with ads. For personalised ads, ad partners may combine this with information from other apps and websites to guess your interests. In the European Economic Area, the UK and Switzerland the game asks for your consent with Google's consent message; without it, ads are not chosen by your interests. In US states with privacy laws, you can also opt out of your information being used for personalised ads. The Remove Ads purchase turns interstitial ads off; rewarded ads stay, for whenever you want one. We measure ad revenue (ad network, ad format, amount) in Firebase Analytics.</p>
<p><strong>Analytics.</strong> To improve the game and balance its difficulty we use Google Firebase Analytics. Analytics processes how you interact with the game (screens opened, levels started, won and lost, session length, purchases, ads watched), device and app information (model, operating system, app version, language), an ID unique to the game's copy on this phone, and the approximate location derived from your IP address (country and city level). In the European Economic Area, the UK and Switzerland, Analytics runs in Google's consent mode and follows the choice you make in the consent message. This information is not matched to your name or email.</p>
<!-- REVIEW: advertising ID in Firebase Analytics and SetUserId: see the Turkish page. -->
<p><strong>Crash reports.</strong> To find and fix bugs we use Firebase Crashlytics. When the game crashes or logs an error, Crashlytics receives the error log, diagnostic information (device model, operating system and app version, memory state, time) and a random installation ID.</p>
<p><strong>Remote settings.</strong> With Firebase Remote Config we change some of the game's settings (how often ads appear, for example) without releasing an update. For this, Firebase uses an ID unique to this installation of the game (the Firebase installation ID).</p>
<p><strong>Support emails.</strong> If you write to us, we use your address and message only to answer you and carry out your request.</p>
<h2>Legal bases</h2>
<ul>
<li><strong>Entering into and performing our contract with you</strong> (KVKK Art. 5(2)(c), GDPR Art. 6(1)(b)): your account, cloud save, purchases and support. They are part of the service you use in the game.</li>
<li><strong>Legitimate interests</strong> (KVKK Art. 5(2)(f), GDPR Art. 6(1)(f)): crash reports, remote settings, showing and measuring ads, preventing fraud; and, in countries where no consent message is shown, analytics and ad personalisation. Keeping the game working, balanced and free to play is our legitimate interest. You can object to this processing, and you can turn off ad personalisation in your phone's ad settings.</li>
<li><strong>Consent</strong> (explicit consent under KVKK Art. 5(1), GDPR Art. 6(1)(a)): personalised ads and analytics in the European Economic Area, the UK and Switzerland, and app tracking on iOS everywhere. You can withdraw your consent at any time.</li>
</ul>
<!-- REVIEW: Türkiye/KVKK consent and the ePrivacy basis for Crashlytics, Remote Config and non-personalised ads: see the Turkish page. -->
<h2>Who receives it</h2>
<p>We don't sell your information for money. For the purposes above, information goes to the companies below; each has its own privacy policy.</p>
<ul>
<li><strong>Google:</strong> Firebase (Analytics, Crashlytics, Remote Config, Authentication, Cloud Firestore), AdMob and Google Play. <a href="https://policies.google.com/privacy">Google Privacy Policy</a>, <a href="https://firebase.google.com/support/privacy">Privacy and security in Firebase</a>, <a href="https://policies.google.com/technologies/partner-sites">How Google uses information from sites or apps that use its services</a>.</li>
<li><strong>Unity:</strong> LevelPlay, Unity Ads and ironSource Ads (ironSource is a Unity company). <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity Game Player and App User Privacy Policy</a>.</li>
<li><strong>Apple:</strong> the App Store and Sign in with Apple. <a href="https://www.apple.com/legal/privacy/">Apple Privacy Policy</a>.</li>
</ul>
<p>In Firebase, Google processes information on our behalf. Ad networks and the stores may also use information for their own purposes under their own policies. Some US state laws count ad partners receiving information for personalised ads as a "sale" or "sharing"; in those states you can opt out in the game's Privacy options row. If the law requires it, we also share information with the competent authorities.</p>
<!-- REVIEW: processor/controller roles, US state law thresholds and the ironSource Ads policy link: see the Turkish page. -->
<h2>Transfers abroad</h2>
<p>Your cloud save is stored in the European Union (Belgium). Google, Unity and Apple also process information outside Türkiye and the European Union, for example in the United States. These transfers rely on the standard contractual clauses these companies use.</p>
<!-- REVIEW: KVKK Art. 9 standard contract (Law No. 7499) and SCCs vs the EU-US Data Privacy Framework: see the Turkish page. -->
<h2>How long we keep it</h2>
<ul>
<li><strong>Account and cloud save:</strong> until you delete them. If the game isn't opened with an account for 24 months, we delete that account and its cloud save.</li>
<li><strong>Analytics:</strong> Analytics event data is deleted after 14 months under our retention setting in Google Analytics. Aggregate figures made from it that identify no one (daily player counts, for example) may be kept longer.</li>
<li><strong>Crash reports:</strong> for as long as Google sets; Crashlytics keeps crash logs and the IDs attached to them for 90 days.</li>
<li><strong>Ad partners:</strong> for the periods in their own policies (linked above).</li>
<li><strong>Purchases:</strong> the items you bought are kept as part of your progress, as above. Apple and Google keep their own purchase records under their own policies.</li>
<li><strong>Support emails:</strong> deleted within a year of the matter being closed.</li>
</ul>
<h2>Your rights</h2>
<p>Under Article 11 of Türkiye's Personal Data Protection Law No. 6698 (KVKK) you can: learn whether your personal data is processed and, if it is, ask for information about it; learn why it is processed and whether it is used for that purpose; know who receives it in Türkiye or abroad; have it corrected if it is incomplete or wrong, and deleted or destroyed where the law's conditions are met, and have those changes passed on to whoever received it; object to a result against you that comes solely from automated analysis; and claim compensation if unlawful processing has harmed you.</p>
<p>If you are in the European Economic Area, the UK or Switzerland, the GDPR and similar laws also give you the right to access your information, have it corrected or deleted, restrict its processing, receive it in a portable format, object to processing based on legitimate interests and withdraw your consent.</p>
<p>To use any of these rights, write to <a href="mailto:{MAIL}">{MAIL}</a> with the player ID shown in the game's settings, so we can find your information. We answer within 30 days, free of charge. If you are not satisfied with our answer, you can complain to the Personal Data Protection Board (KVKK) in Türkiye, or to the data protection authority of the country you live in in Europe.</p>
<!-- REVIEW: KVKK application channels for players with anonymous accounts: see the Turkish page. -->
<h2>Withdrawing consent</h2>
<p>Where the consent message is shown (the European Economic Area, the UK, Switzerland and some US states), a <strong>Privacy options</strong> row appears in the game's Settings; you can change your choice there at any time. Everywhere, you can also use your phone's settings: on iOS, turn off tracking for the game in Settings → Privacy &amp; Security → Tracking; on Android, delete or reset your advertising ID in the ads section of your phone's settings. Withdrawing consent does not affect processing that took place before.</p>
<h2>Deleting your account</h2>
<p>You can delete your account and cloud save in the game: <strong>Settings → Cloud save → Delete account</strong>. If you can't open the game, you can email us. What is deleted, what remains and how long it takes is on the <a href="delete-account.html">account deletion page</a>.</p>
<h2>Children</h2>
<p>Our games are not directed at children under 13, and we do not knowingly collect information from them. If you think a child under 13 has given us information, write to us and we will delete it.</p>
<!-- REVIEW: GDPR Art. 8 age of digital consent (13-16 by country) and minors under Turkish law: see the Turkish page. -->
<h2>Changes</h2>
<p>If we change this policy, we publish the new version on this page with its new date.</p>
</article>''',
}

# The account-deletion pages: Google Play's Data safety form asks for this URL (spec §3.5); Apple's 5.1.1(v) asks for in-app deletion.
DELETE = {
    "tr": f'''<article class="prose">
<h1>Hesap silme</h1>
<p>Bu sayfa, Symbol Interactive'in oyunu <strong>Yıldız Kavanozu</strong>'ndaki (mağazalarda <strong>Star Jars Sort Deluxe</strong>) hesabını ve bulut kaydını nasıl sileceğini anlatır. Geliştirici: {CONTROLLER["tr"]} (Symbol Interactive).</p>
<!-- REVIEW (not legal): the labels Ayarlar → Bulut kaydı → Hesabı sil and "oyuncu kimliği" must match the game's final Turkish strings (Plan 5f screens). -->
<h2>Oyunun içinden</h2>
<ol>
<li>Oyunda <strong>Ayarlar</strong>'ı aç.</li>
<li><strong>Bulut kaydı</strong> bölümüne dokun.</li>
<li><strong>Hesabı sil</strong>'e dokun ve silmeyi onayla.</li>
</ol>
<p>Hesabın ve bulut kaydın o anda silinir. Bu telefondaki ilerlemen kalır ve oyun onunla devam eder; onu da silmek istersen oyunu telefonundan kaldır.</p>
<!-- REVIEW (product, changes this text): confirm what the game does after a deletion. If it opens a new anonymous account and uploads the local progress again, say so here and offer a way to delete the local progress too. -->
<h2>E-postayla</h2>
<p>Oyunu açamıyorsan ya da silmeyi bizim yapmamızı istersen, <a href="mailto:{MAIL}?subject=Hesap%20silme">{MAIL}</a> adresine konusu <strong>Hesap silme</strong> olan bir e-posta gönder ve oyunun Ayarlar ekranında görünen <strong>oyuncu kimliğini</strong> ekle. Hesabını bu kimlikle buluruz.</p>
<p>Oyunu sildiğin için kimliğini göremiyorsan: hesabını Apple ya da Google ile bağladıysan oyunu yeniden yükleyip aynı hesapla giriş yap; kimliğin Ayarlar'da yine görünür ve silmeyi oradan kendin de yapabilirsin. Hesabını hiç bağlamadıysan, anonim hesap yalnızca o telefondaki oyuna bağlıydı ve hangi hesabın senin olduğunu bilemeyiz; böyle bir hesap 24 ay kullanılmadığında kendiliğinden silinir.</p>
<h2>Neler silinir</h2>
<ul>
<li><strong>Bulut kaydın:</strong> Cloud Firestore'daki kayıt belgen; içindeki ilerlemen, ayarların, ilerleme özetin, cihaz modelin ve kayıt zamanları.</li>
<li><strong>Firebase hesabın:</strong> anonim hesap kimliğin ve, bağladıysan, Apple ya da Google hesabınla olan bağlantısı.</li>
</ul>
<p>Silinen bulut kaydı geri getirilemez. Reklamsız gibi kalıcı satın almalar mağaza hesabına bağlıdır; aynı App Store ya da Google Play hesabıyla geri yükleyebilirsin.</p>
<h2>Neler kalır</h2>
<ul>
<li><strong>Analitik ve çökme verileri:</strong> Firebase Analytics ve Crashlytics'teki kayıtlar oyundaki hesabına değil, oyunun telefondaki kopyasına özgü bir kimliğe bağlıdır ve kendiliğinden silinir: Analytics olayları 14 ay, çökme kayıtları 90 gün sonra. Bunlardan üretilmiş, kimseyi tanıtmayan toplu ve anonim sayılar (örneğin günlük oyuncu sayısı) kalır.</li>
<li><strong>Reklam ortaklarının verileri:</strong> Unity (LevelPlay, Unity Ads, ironSource Ads) ve Google AdMob, reklam için işledikleri bilgileri kendi politikalarına göre saklar ve siler: <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity</a>, <a href="https://policies.google.com/privacy">Google</a>. Bu bilgiler oyundaki hesabına bağlı değildir; telefonunun ayarlarından reklam kimliğini silebilir ya da sıfırlayabilirsin.</li>
<li><strong>Mağaza satın alma kayıtları:</strong> Apple ve Google, satın almalarının kayıtlarını kendi politikalarına göre tutar.</li>
<li><strong>Yazışmalar:</strong> silme için bize yazdıysan, yazışmamız iş bittikten sonra en geç bir yıl içinde silinir.</li>
</ul>
<h2>Ne kadar sürer</h2>
<p>Silme en geç 30 gün içinde tamamlanır. Oyunun içinden istediğinde hesabın ve bulut kaydın o anda silinir; e-postayla istediğinde en geç 30 gün içinde siler, bittiğinde sana haber veririz. Google, silinen verilerin yedek sistemlerindeki kopyalarını kendi takvimine göre ayrıca temizler.</p>
<!-- REVIEW: Firebase's privacy page says deleted Authentication data leaves Google's live and backup systems within 180 days. Decide whether to state the 180 days here; either way, our own deletion is done within 30 days. -->
<p>Bilgilerinin nasıl işlendiği <a href="gizlilik.html">gizlilik politikasında</a>. Soruların için: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
</article>''',
    "en": f'''<article class="prose">
<h1>Deleting your account</h1>
<p>This page explains how to delete your account and cloud save in <strong>Star Jars Sort Deluxe</strong> (Yıldız Kavanozu in Turkish), a game by Symbol Interactive. Developer: {CONTROLLER["en"]} (Symbol Interactive).</p>
<!-- REVIEW (not legal): the labels Settings → Cloud save → Delete account and "Player ID" must match the game's final English strings (Plan 5f screens). -->
<h2>In the game</h2>
<ol>
<li>Open <strong>Settings</strong> in the game.</li>
<li>Tap <strong>Cloud save</strong>.</li>
<li>Tap <strong>Delete account</strong> and confirm.</li>
</ol>
<p>Your account and cloud save are deleted at once. The progress on this phone stays and the game carries on with it; to remove that too, uninstall the game.</p>
<!-- REVIEW (product, changes this text): what the game does after a deletion: see the Turkish page. -->
<h2>By email</h2>
<p>If you can't open the game, or would rather we did it, email <a href="mailto:{MAIL}?subject=Account%20deletion">{MAIL}</a> with the subject line <strong>Account deletion</strong> and include the <strong>player ID</strong> shown in the game's Settings. We find your account by that ID.</p>
<p>If you can't see your ID because you deleted the game: if you linked your account to Apple or Google, install the game again and sign in with the same account; your ID appears in Settings again, and you can delete the account there yourself. If you never linked it, the anonymous account belonged only to the game on that phone and we cannot tell which account is yours; such an account is deleted on its own after 24 months without use.</p>
<h2>What is deleted</h2>
<ul>
<li><strong>Your cloud save:</strong> your save document in Cloud Firestore, with your progress, settings, progress summary, device model and save times.</li>
<li><strong>Your Firebase account:</strong> your anonymous account ID and, if you linked one, its link to your Apple or Google account.</li>
</ul>
<p>A deleted cloud save cannot be brought back. Permanent purchases such as Remove Ads belong to your store account; you can restore them with the same App Store or Google Play account.</p>
<h2>What remains</h2>
<ul>
<li><strong>Analytics and crash data:</strong> records in Firebase Analytics and Crashlytics are tied not to your game account but to an ID unique to the game's copy on your phone, and they are deleted on their own: Analytics events after 14 months, crash logs after 90 days. Aggregate, anonymous figures made from them that identify no one (daily player counts, for example) remain.</li>
<li><strong>Ad partners' data:</strong> Unity (LevelPlay, Unity Ads, ironSource Ads) and Google AdMob keep and delete what they processed for ads under their own policies: <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity</a>, <a href="https://policies.google.com/privacy">Google</a>. This information is not tied to your game account; you can delete or reset your advertising ID in your phone's settings.</li>
<li><strong>Store purchase records:</strong> Apple and Google keep records of your purchases under their own policies.</li>
<li><strong>Emails:</strong> if you wrote to us to delete your account, the emails we exchanged are deleted within a year of the matter being closed.</li>
</ul>
<h2>How long it takes</h2>
<p>Deletion is done within 30 days. In the game, your account and cloud save are deleted at once; by email, we delete them within 30 days and let you know when it's done. Google separately clears copies of deleted data from its backup systems on its own schedule.</p>
<!-- REVIEW: Google's 180-day backup removal: see the Turkish page. -->
<p>How your information is processed is in the <a href="privacy.html">privacy policy</a>. Questions: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
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
page("tr", "hesap-silme.html", "Hesap silme · Symbol Interactive", "Yıldız Kavanozu hesabını ve bulut kaydını silme.", DELETE["tr"], "en/delete-account.html")
page("en", "en/delete-account.html", "Delete account · Symbol Interactive", "How to delete your Star Jars Sort Deluxe account and cloud save.", DELETE["en"], "../hesap-silme.html")
# The App Store's support and marketing URLs (the user, 2026-11-03): /support and /starjars, in both languages on one page each.
SUPPORT_BOTH = SUPPORT["en"].replace('href="privacy.html"', 'href="en/privacy.html"').replace('href="delete-account.html"', 'href="en/delete-account.html"') +SUPPORT["tr"].replace("<h1>Destek</h1>", '<h2 class="lang" lang="tr">Türkçe</h2>').replace('<article class="prose">', '<article class="prose" lang="tr">')
page("en", "support.html", "Support · Symbol Interactive", "Support for Symbol Interactive games.", SUPPORT_BOTH, "destek.html")
def shots(lang):
    return "".join(f'<img src="img/{lang}-{n}.jpg" width="270" height="587" alt="" loading="lazy">' for n in ["01-board", "03-galaxy", "04-exo"])
STARJARS = f'''<section class="hero">
  <div>
    <h1>Star Jars Sort Deluxe</h1>
    <p class="lede">A calm puzzle where you sort colorful stars into jars. Every sealed jar lights a star of a real constellation: 136 levels across 18 constellations, star cards with real facts, and space chapters with their own rules.</p>
    <p class="status">Coming soon to the App Store and Google Play. In thirteen languages.</p>
  </div>
  {{jar()}}
</section>
<div class="shots">{{shots("en")}}</div>
<section class="prose" lang="tr">
  <h2>Yıldız Kavanozu</h2>
  <p>Renkli yıldızları kavanozlara ayırdığın sakin bir bulmaca. Her mühürlenen kavanoz gerçek bir takımyıldızının yıldızını yakar: 18 takımyıldızında 136 seviye, gerçek bilgilerle yıldız kartları ve kendi kuralıyla uzay bölümleri.</p>
  <p class="status">Yakında App Store ve Google Play'de. On üç dilde.</p>
</section>
<div class="shots">{{shots("tr")}}</div>'''
page("en", "starjars.html", "Star Jars Sort Deluxe · Symbol Interactive", "Star Jars Sort Deluxe: sort the stars, light up the constellations.", STARJARS.replace("{jar()}", jar()).replace('{shots("en")}', shots("en")).replace('{shots("tr")}', shots("tr")), "index.html")
page("tr", "404.html", "Sayfa yok · Symbol Interactive", "Sayfa bulunamadı.", NOT_FOUND, "/en/")
(ROOT / "favicon.svg").write_text(jar("fav", animate=False).replace('class="fav" ', 'xmlns="http://www.w3.org/2000/svg" '), encoding="utf-8")
(ROOT / "CNAME").write_text("symbolinteractive.com.tr\n", encoding="utf-8")
app_ads = ROOT / "app-ads.txt"
if not app_ads.exists():  # the ad networks' lines come with the real ads (LevelPlay); never overwritten here
    app_ads.write_text("# Symbol Interactive: authorized sellers of our apps' ad inventory (IAB app-ads.txt). Lines are added with the ad networks.\n", encoding="utf-8")
review = sum(f.read_text(encoding="utf-8").count("<!-- REVIEW") for f in [*ROOT.glob("*.html"), *ROOT.glob("en/*.html")])
print(f"built; {review} REVIEW notes still in the pages (settle and remove them before this goes live)" if review else "built")
