import html
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCX = Path.home() / "Downloads" / "EKSPECTO EN FRANCAIS.docx"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

LANGUAGES = [
    ("", "Selectionner une langue"),
    ("ab", "Abkhaze"), ("ace", "Aceh"), ("ach", "Acholi"), ("aa", "Afar"),
    ("af", "Afrikaans"), ("sq", "Albanais"), ("de", "Allemand"),
    ("alz", "Alur"), ("am", "Amharique"), ("en", "Anglais"), ("ar", "Arabe"),
    ("hy", "Armenien"), ("as", "Assamais"), ("av", "Avar"), ("awa", "Awadhi"),
    ("ay", "Aymara"), ("az", "Azeri"), ("ba", "Bachkir"), ("ban", "Balinais"),
    ("bm", "Bambara"), ("eu", "Basque"), ("bn", "Bengali"), ("bho", "Bhojpuri"),
    ("be", "Bielorusse"), ("my", "Birman"), ("bs", "Bosniaque"),
    ("bg", "Bulgare"), ("ca", "Catalan"), ("ceb", "Cebuano"),
    ("ny", "Chichewa"), ("zh-CN", "Chinois simplifie"), ("zh-TW", "Chinois traditionnel"),
    ("ko", "Coreen"), ("co", "Corse"), ("ht", "Creole haitien"), ("hr", "Croate"),
    ("da", "Danois"), ("es", "Espagnol"), ("eo", "Esperanto"), ("et", "Estonien"),
    ("ee", "Ewe"), ("fi", "Finnois"), ("fr", "Francais"), ("fy", "Frison"),
    ("gd", "Gaelique ecossais"), ("cy", "Gallois"), ("ka", "Georgien"),
    ("el", "Grec"), ("gn", "Guarani"), ("gu", "Gujarati"), ("ha", "Haoussa"),
    ("haw", "Hawaiien"), ("iw", "Hebreu"), ("hi", "Hindi"), ("hmn", "Hmong"),
    ("hu", "Hongrois"), ("ig", "Igbo"), ("ilo", "Ilocano"), ("id", "Indonesien"),
    ("ga", "Irlandais"), ("is", "Islandais"), ("it", "Italien"), ("ja", "Japonais"),
    ("jw", "Javanais"), ("kn", "Kannada"), ("kk", "Kazakh"), ("km", "Khmer"),
    ("rw", "Kinyarwanda"), ("ky", "Kirghiz"), ("ku", "Kurde"), ("lo", "Lao"),
    ("la", "Latin"), ("lv", "Letton"), ("ln", "Lingala"), ("lt", "Lituanien"),
    ("lb", "Luxembourgeois"), ("mk", "Macedonien"), ("ms", "Malais"),
    ("ml", "Malayalam"), ("mg", "Malgache"), ("mt", "Maltais"), ("mi", "Maori"),
    ("mr", "Marathi"), ("mn", "Mongol"), ("ne", "Nepalais"), ("nl", "Neerlandais"),
    ("no", "Norvegien"), ("or", "Odia"), ("ug", "Ouighour"), ("ur", "Ourdou"),
    ("uz", "Ouzbek"), ("ps", "Pachto"), ("fa", "Persan"), ("pl", "Polonais"),
    ("pt", "Portugais"), ("pa", "Punjabi"), ("ro", "Roumain"), ("ru", "Russe"),
    ("sm", "Samoan"), ("sr", "Serbe"), ("st", "Sesotho"), ("sn", "Shona"),
    ("sd", "Sindhi"), ("si", "Singhalais"), ("sk", "Slovaque"), ("sl", "Slovene"),
    ("so", "Somali"), ("su", "Soundanais"), ("sv", "Suedois"), ("sw", "Swahili"),
    ("tg", "Tadjik"), ("ta", "Tamoul"), ("cs", "Tcheque"), ("te", "Telougou"),
    ("th", "Thai"), ("ti", "Tigrigna"), ("tr", "Turc"), ("tk", "Turkmene"),
    ("uk", "Ukrainien"), ("vi", "Vietnamien"), ("yi", "Yiddish"), ("yo", "Yoruba"),
    ("zu", "Zoulou"),
]


def attr(element, name):
    return element.get(W + name) if element is not None else None


def text_content(paragraph):
    parts = []
    for node in paragraph.iter():
        if node.tag == W + "t":
            parts.append(node.text or "")
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag == W + "br":
            parts.append("\n")
    return "".join(parts)


def paragraph_alignment(paragraph):
    ppr = paragraph.find(W + "pPr")
    if ppr is None:
        return ""
    jc = ppr.find(W + "jc")
    value = attr(jc, "val")
    return value or ""


def run_html(run):
    pieces = []
    for node in run:
        if node.tag == W + "t":
            pieces.append(linkify(html.escape(node.text or "", quote=False)))
        elif node.tag == W + "tab":
            pieces.append("&nbsp;&nbsp;&nbsp;&nbsp;")
        elif node.tag == W + "br":
            pieces.append("<br>")
    content = "".join(pieces)
    if not content:
        return ""

    rpr = run.find(W + "rPr")
    classes = []
    styles = []
    if rpr is not None:
        if rpr.find(W + "b") is not None:
            classes.append("bold")
        if rpr.find(W + "i") is not None:
            classes.append("italic")
        color = attr(rpr.find(W + "color"), "val")
        if color and color.lower() != "auto":
            styles.append(f"color:#{color};")
    if not classes and not styles:
        return content
    class_attr = f' class="{" ".join(classes)}"' if classes else ""
    style_attr = f' style="{" ".join(styles)}"' if styles else ""
    return f"<span{class_attr}{style_attr}>{content}</span>"


def paragraph_inner_html(paragraph):
    pieces = []
    for child in paragraph:
        if child.tag == W + "r":
            pieces.append(run_html(child))
        elif child.tag == W + "hyperlink":
            pieces.extend(run_html(run) for run in child.findall(W + "r"))
    return "".join(pieces)


def linkify(escaped_text):
    pattern = r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
    return re.sub(pattern, r'<a href="mailto:\1">\1</a>', escaped_text)


def paragraph_html(paragraph, source_index):
    raw_text = text_content(paragraph)
    if not raw_text.strip():
        return ""
    inner = paragraph_inner_html(paragraph)
    normalized = re.sub(r"\s+", " ", raw_text).strip()
    classes = ["doc-paragraph"]
    align = paragraph_alignment(paragraph)
    if align == "center" or source_index in (1, 4):
        classes.append("center")
    if source_index == 1:
        return f'<h1 class="main-title">{inner}</h1>'
    if source_index == 2:
        return f'<p class="copyright">{inner}</p>'
    if source_index == 3:
        return f'<p class="club-line">{inner}</p>'
    if source_index == 4:
        return f'<div class="origin-block">{inner}</div>'
    if source_index == 5:
        return f'<p class="construction-note">{inner}</p>'
    if normalized.upper().startswith(("NOTE", "NOTA", "UN CONSEIL")):
        classes.append("note")
    if normalized.upper().startswith("NOTE IMPORTANTE"):
        classes.append("important-note")
    if normalized == "A propos d'ekspecto.com":
        classes.append("about-section-title")
    if normalized.startswith("- ") or re.match(r"^-?\s*\d+[. ]", normalized):
        classes.append("list-like")
    if "color:#C00000" in inner or "color:#FF0000" in inner or "color:#ff0000" in inner:
        classes.append("red-paragraph")
    return f'<p class="{" ".join(classes)}">{inner}</p>'


def read_docx():
    with zipfile.ZipFile(DOCX) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    paragraphs = []
    source_index = 1
    for paragraph in root.iter(W + "p"):
        rendered = paragraph_html(paragraph, source_index)
        if rendered:
            paragraphs.append(rendered)
            source_index += 1
    if len(paragraphs) >= 5:
        paragraphs = paragraphs[:3] + [paragraphs[4], paragraphs[3]] + paragraphs[5:]
    return paragraphs


def build_index(content):
    options = "\n".join(
        f'          <option value="{html.escape(code)}">{html.escape(label)}</option>'
        for code, label in LANGUAGES
    )
    included_languages = ",".join(code for code, _ in LANGUAGES if code)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="A propos d'ekspecto.com">
  <title>A propos d'ekspecto.com</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="language-box" aria-label="Choix de langue">
    <p>Pour choisir une autre<br>langue, CLIQUEZ ICI</p>
    <select id="language-select" aria-label="Selectionner une langue">
{options}
    </select>
    <span class="google-note">Fourni par <span class="google-word"><span>G</span><span>o</span><span>o</span><span>g</span><span>l</span><span>e</span></span> Traduction</span>
  </div>
  <div id="google_translate_element" aria-hidden="true"></div>

  <main class="page">
    <article class="content">
{content}
    </article>
  </main>

  <div class="scroll-buttons" aria-label="Boutons de navigation">
    <button type="button" id="scroll-up" aria-label="Aller en haut">&#9650;</button>
    <button type="button" id="scroll-middle" aria-label="Defiler vers le bas"></button>
    <button type="button" id="scroll-down" aria-label="Aller en bas">&#9660;</button>
  </div>

  <script>
    function googleTranslateElementInit() {{
      new google.translate.TranslateElement({{
        pageLanguage: 'fr',
        includedLanguages: '{included_languages}',
        autoDisplay: false
      }}, 'google_translate_element');
    }}
  </script>
  <script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
  <script src="script.js"></script>
</body>
</html>
"""


STYLE = """@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

html {
  scroll-behavior: smooth;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  overflow-x: hidden;
  background: #ffffff;
  color: #000;
  font-family: "Montserrat", sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 1.55;
}

.page {
  width: 100%;
  padding: 76px 24px 38px;
  background: #ffffff;
}

.content {
  width: min(950px, calc(100% - 40px));
  margin: 0 auto;
  background: #ffffff;
}

.main-title {
  width: 360px;
  max-width: 100%;
  margin: 0 auto 18px;
  text-align: center;
  color: #e40046;
  font-family: "Montserrat", sans-serif;
  font-size: 34px;
  font-weight: 700;
  line-height: 0.95;
}

.copyright {
  margin: 0 0 34px;
  text-align: center;
  font-size: 13px;
  font-style: italic;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.club-line {
  margin: 0 0 18px;
  text-align: center;
  color: #ff0000;
  font-size: 17px;
  font-weight: 700;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.construction-note {
  margin: 0 0 30px;
  text-align: center;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.origin-block {
  max-width: 950px;
  margin: 0 auto 27px;
  text-align: center;
  font-size: 13px;
  font-style: italic;
  line-height: 1.48;
  overflow-wrap: anywhere;
}

.doc-paragraph {
  margin: 0 0 17px;
  font-size: 13px;
  line-height: 1.58;
  text-align: justify;
  text-justify: inter-word;
  overflow-wrap: anywhere;
}

.doc-paragraph span,
.doc-paragraph a {
  overflow-wrap: anywhere;
}

.doc-paragraph.center {
  text-align: center;
}

.doc-paragraph.note {
  margin-top: 20px;
  font-size: 13px;
  line-height: 1.58;
}

.doc-paragraph.important-note {
  font-size: 15px;
  line-height: 1.45;
}

.doc-paragraph.list-like {
  margin-bottom: 17px;
  font-size: 13px;
  line-height: 1.58;
  text-align: left;
}

.bold {
  font-weight: 700;
  font-size: 15px;
}

.doc-paragraph.red-paragraph {
  margin-bottom: 8px;
  font-size: 17px;
  line-height: 1.36;
}

span[style*="color:#C00000"],
span[style*="color:#FF0000"],
span[style*="color:#ff0000"] {
  font-size: 17px;
  line-height: 1.36;
}

.doc-paragraph.about-section-title {
  margin-top: 32px;
  margin-bottom: 26px;
}

.italic {
  font-style: italic;
}

a,
.email {
  color: #0000ee;
}

a {
  text-decoration: none;
}

.language-box {
  position: fixed;
  top: 28px;
  right: 44px;
  z-index: 10;
  width: 225px;
  text-align: center;
  font-size: 13px;
  line-height: 1.22;
}

.language-box p {
  margin: 0 0 8px;
  font-weight: 700;
}

.language-box select {
  width: 100%;
  height: 22px;
  border: 2px solid #111;
  border-radius: 3px;
  background: #fff;
  color: #000;
  font: 12px "Montserrat", sans-serif;
}

.google-note {
  display: block;
  margin-top: 4px;
  color: #777;
  font-size: 11px;
}

.google-word span:nth-child(1),
.google-word span:nth-child(4) {
  color: #4285f4;
}

.google-word span:nth-child(2),
.google-word span:nth-child(6) {
  color: #db4437;
}

.google-word span:nth-child(3) {
  color: #f4b400;
}

.google-word span:nth-child(5) {
  color: #0f9d58;
}

#google_translate_element,
.goog-te-banner-frame,
iframe.goog-te-banner-frame,
.goog-te-gadget-icon {
  display: none !important;
}

body {
  top: 0 !important;
}

.scroll-buttons {
  position: fixed;
  right: 7%;
  top: 35%;
  bottom: 22px;
  z-index: 20;
  width: 18px;
  pointer-events: none;
}

#scroll-middle {
  position: absolute;
  top: 28px;
  left: 50%;
  width: 16px;
  height: 34px;
  padding: 0;
  border: 0;
  border-radius: 12px;
  background: transparent;
  transform: translateX(-50%);
  pointer-events: auto;
  touch-action: none;
  cursor: ns-resize;
}

#scroll-middle::before {
  content: "";
  display: block;
  width: 9px;
  height: 26px;
  margin: 4px auto;
  border-radius: 9px;
  background: #ff6f7c;
}

.scroll-buttons button {
  width: 18px;
  height: 18px;
  padding: 0;
  border: 0;
  background: transparent;
  color: #ff6f7c;
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
  text-align: center;
  pointer-events: auto;
}

#scroll-up {
  position: absolute;
  top: 0;
  left: 0;
}

#scroll-down {
  position: absolute;
  left: 0;
  bottom: 0;
}

@media (max-width: 1200px) {
  .content {
    width: min(950px, calc(100% - 300px));
    margin: 0 auto;
  }

  .scroll-buttons {
    right: 24px;
  }
}

@media (max-width: 900px) {
  body {
    font-size: 13px;
  }

  .page {
    padding: 18px 24px 42px 14px;
  }

  .content {
    width: calc(100vw - 38px);
    max-width: 950px;
    margin: 0 auto;
  }

  .language-box {
    position: static;
    width: min(260px, calc(100% - 20px));
    margin: 12px auto 10px;
  }

  .main-title {
    margin-top: 8px;
    font-size: 31px;
  }

  .scroll-buttons {
    right: 10px;
    top: 34%;
    bottom: 18px;
  }
}

@media (max-width: 520px) {
  body {
    font-size: 13px;
    line-height: 1.58;
  }

  .page {
    padding: 8px 24px 68px 10px;
  }

  .content {
    width: calc(100vw - 34px);
  }

  .main-title {
    width: 280px;
    font-size: 27px;
    margin-bottom: 18px;
  }

  .copyright {
    font-size: 13px;
    line-height: 1.45;
  }

  .club-line {
    font-size: 17px;
    line-height: 1.35;
  }

  .construction-note {
    font-size: 15px;
    line-height: 1.45;
  }

  .origin-block {
    font-size: 13px;
    line-height: 1.48;
  }

  .doc-paragraph {
    font-size: 13px;
    margin-bottom: 15px;
  }

  .doc-paragraph.note,
  .doc-paragraph.list-like {
    font-size: 13px;
  }

  .doc-paragraph.important-note {
    font-size: 15px;
  }

  .doc-paragraph.red-paragraph,
  span[style*="color:#C00000"],
  span[style*="color:#FF0000"],
  span[style*="color:#ff0000"] {
    font-size: 17px;
  }

  .scroll-buttons {
    right: 4px;
    top: 32%;
    bottom: 14px;
    width: 16px;
  }

  #scroll-middle {
    width: 16px;
    height: 32px;
  }

  #scroll-middle::before {
    width: 8px;
    height: 24px;
  }

  .scroll-buttons button {
    width: 16px;
    height: 18px;
    font-size: 13px;
  }
}

@media (max-width: 360px) {
  body {
    font-size: 13px;
  }

  .page {
    padding-left: 8px;
    padding-right: 22px;
  }

  .content {
    width: calc(100vw - 30px);
  }

  .main-title {
    width: 250px;
    font-size: 25px;
  }

  .language-box {
    width: calc(100% - 18px);
  }

  .language-box select {
    font-size: 12px;
  }
}
"""


SCRIPT = """const languageSelect = document.getElementById('language-select');
const scrollUp = document.getElementById('scroll-up');
const scrollMiddle = document.getElementById('scroll-middle');
const scrollDown = document.getElementById('scroll-down');
const scrollButtons = document.querySelector('.scroll-buttons');
let middleDragOffset = 0;
let middleIsDragging = false;

const setTranslateCookie = (targetLanguage) => {
  const value = `/fr/${targetLanguage || 'fr'}`;
  const host = window.location.hostname;
  document.cookie = `googtrans=${value}; path=/`;
  if (host && host.includes('.')) {
    const rootDomain = host.split('.').slice(-2).join('.');
    document.cookie = `googtrans=${value}; path=/; domain=.${rootDomain}`;
  }
};

const applyLanguage = (targetLanguage, attempt = 0) => {
  setTranslateCookie(targetLanguage);
  document.documentElement.lang = targetLanguage || 'fr';
  const combo = document.querySelector('.goog-te-combo');
  if (!combo) {
    if (attempt < 40) {
      window.setTimeout(() => applyLanguage(targetLanguage, attempt + 1), 250);
    }
    return;
  }
  combo.value = targetLanguage;
  combo.dispatchEvent(new Event('change'));
};

const getScrollTop = () => window.scrollY || document.documentElement.scrollTop;

const getScrollMax = () => Math.max(
    document.body.scrollHeight,
    document.documentElement.scrollHeight
  ) - window.innerHeight;

const setScrollTop = (top, behavior = 'smooth') => {
  window.scrollTo({ top, behavior });
};

const getMiddleTrack = () => {
  if (!scrollButtons || !scrollMiddle) return null;
  const container = scrollButtons.getBoundingClientRect();
  const top = 28;
  const bottom = container.height - 34;
  const maxTop = Math.max(top, bottom - scrollMiddle.offsetHeight);
  return { container, top, maxTop };
};

const updateMiddlePosition = () => {
  const track = getMiddleTrack();
  if (!track || middleIsDragging) return;
  const maxScroll = getScrollMax();
  const percent = maxScroll > 0 ? getScrollTop() / maxScroll : 0;
  const nextTop = track.top + (track.maxTop - track.top) * percent;
  scrollMiddle.style.top = `${nextTop}px`;
};

if (languageSelect) {
  languageSelect.addEventListener('change', () => {
    const targetLanguage = languageSelect.value;
    if (!targetLanguage) return;
    applyLanguage(targetLanguage);
  });
}

if (scrollUp) {
  scrollUp.addEventListener('click', () => {
    setScrollTop(0);
  });
}

if (scrollMiddle) {
  scrollMiddle.addEventListener('click', () => {
    updateMiddlePosition();
  });

  scrollMiddle.addEventListener('pointerdown', (event) => {
    const rect = scrollMiddle.getBoundingClientRect();
    middleDragOffset = event.clientY - rect.top;
    middleIsDragging = true;
    scrollMiddle.setPointerCapture(event.pointerId);
    event.preventDefault();
  });

  scrollMiddle.addEventListener('pointermove', (event) => {
    if (!middleIsDragging) return;
    const track = getMiddleTrack();
    if (!track) return;
    const rawTop = event.clientY - track.container.top - middleDragOffset;
    const nextTop = Math.min(track.maxTop, Math.max(track.top, rawTop));
    const range = track.maxTop - track.top;
    const percent = range > 0 ? (nextTop - track.top) / range : 0;
    scrollMiddle.style.top = `${nextTop}px`;
    setScrollTop(getScrollMax() * percent, 'auto');
  });

  scrollMiddle.addEventListener('pointerup', () => {
    middleIsDragging = false;
    updateMiddlePosition();
  });

  scrollMiddle.addEventListener('pointercancel', () => {
    middleIsDragging = false;
    updateMiddlePosition();
  });
}

if (scrollDown) {
  scrollDown.addEventListener('click', () => {
    setScrollTop(getScrollMax());
  });
}

window.addEventListener('scroll', updateMiddlePosition, { passive: true });
window.addEventListener('resize', updateMiddlePosition);
updateMiddlePosition();
"""


def main():
    paragraphs = read_docx()
    content = "\n".join(f"      {paragraph}" for paragraph in paragraphs)
    (ROOT / "index.html").write_text(build_index(content), encoding="utf-8")
    (ROOT / "style.css").write_text(STYLE, encoding="utf-8")
    (ROOT / "script.js").write_text(SCRIPT, encoding="utf-8")
    print(f"Generated index.html with {len(paragraphs)} paragraphs from {DOCX}")


if __name__ == "__main__":
    main()
