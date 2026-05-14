import html
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCX = Path(r"c:\Users\HP\Downloads\EKSPECTO EN FRANCAIS.docx")
NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

LANGS = [
    ("FR", "fr", "FR", "&#x1F1EB;&#x1F1F7;", "Français", "Français"),
    ("AR", "ar", "SA", "&#x1F1F8;&#x1F1E6;", "العربية", "العربية"),
    ("EN", "en", "GB", "&#x1F1EC;&#x1F1E7;", "English", "English"),
    ("ES", "es", "ES", "&#x1F1EA;&#x1F1F8;", "Español", "Español"),
    ("IT", "it", "IT", "&#x1F1EE;&#x1F1F9;", "Italiano", "Italiano"),
    ("DE", "de", "DE", "&#x1F1E9;&#x1F1EA;", "Deutsch", "Deutsch"),
    ("PT", "pt", "PT", "&#x1F1F5;&#x1F1F9;", "Português", "Português"),
    ("NL", "nl", "NL", "&#x1F1F3;&#x1F1F1;", "Nederlands", "Nederlands"),
    ("RU", "ru", "RU", "&#x1F1F7;&#x1F1FA;", "Русский", "Русский"),
    ("ZH", "zh", "CN", "&#x1F1E8;&#x1F1F3;", "中文", "中文"),
    ("JA", "ja", "JP", "&#x1F1EF;&#x1F1F5;", "日本語", "日本語"),
    ("KO", "ko", "KR", "&#x1F1F0;&#x1F1F7;", "한국어", "한국어"),
    ("TR", "tr", "TR", "&#x1F1F9;&#x1F1F7;", "Türkçe", "Türkçe"),
    ("HI", "hi", "IN", "&#x1F1EE;&#x1F1F3;", "हिन्दी", "हिन्दी"),
    ("RO", "ro", "RO", "&#x1F1F7;&#x1F1F4;", "Română", "Română"),
    ("UK", "uk", "UA", "&#x1F1FA;&#x1F1E6;", "Українська", "Українська"),
    ("PL", "pl", "PL", "&#x1F1F5;&#x1F1F1;", "Polski", "Polski"),
    ("SV", "sv", "SE", "&#x1F1F8;&#x1F1EA;", "Svenska", "Svenska"),
    ("NO", "no", "NO", "&#x1F1F3;&#x1F1F4;", "Norsk", "Norsk"),
    ("DA", "da", "DK", "&#x1F1E9;&#x1F1F0;", "Dansk", "Dansk"),
    ("EL", "el", "GR", "&#x1F1EC;&#x1F1F7;", "Ελληνικά", "Ελληνικά"),
    ("ID", "id", "ID", "&#x1F1EE;&#x1F1E9;", "Bahasa Indonesia", "Bahasa Indonesia"),
    ("VI", "vi", "VN", "&#x1F1FB;&#x1F1F3;", "Tiếng Việt", "Tiếng Việt"),
    ("TH", "th", "TH", "&#x1F1F9;&#x1F1ED;", "ภาษาไทย", "ภาษาไทย"),
    ("HE", "he", "IL", "&#x1F1EE;&#x1F1F1;", "עברית", "עברית"),
]


def docx_paragraphs():
    with zipfile.ZipFile(DOCX) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    paragraphs = []
    for p in root.iter(NS + "p"):
        parts = []
        for node in p.iter():
            if node.tag == NS + "t":
                parts.append(node.text or "")
            elif node.tag == NS + "tab":
                parts.append("\t")
            elif node.tag == NS + "br":
                parts.append("\n")
        text = "".join(parts)
        if text.strip():
            paragraphs.append(text)
    return paragraphs


def compact(text):
    return re.sub(r"\s+", " ", text).strip()


def callout_class(text):
    value = text.strip().upper()
    if value.startswith("NOTE TRES IMPORTANTE") or "TRÈS IMPORTANT" in value[:90] or "TRES IMPORTANT" in value[:90]:
        return "callout-critical"
    if value.startswith("NOTE") or value.startswith("NOTA") or value.startswith("UN CONSEIL"):
        return "callout-warning"
    if value.startswith("IMPORTANT") or value.startswith("ATTENTION"):
        return "callout-critical"
    if value.startswith("EXEMPLE") or value.startswith("POURQUOI") or value.startswith("COMMENT"):
        return "callout-info"
    return ""


def titleish(text):
    value = compact(text)
    return len(value) <= 72 and not value.endswith((".", ",", ";"))


def build():
    paragraphs = docx_paragraphs()
    toc_items = []
    sections = []
    for idx, text in enumerate(paragraphs, 1):
        section_id = f"section-{idx}"
        label = compact(text)
        if len(label) > 70:
            label = label[:67].rstrip() + "..."
        toc_items.append(f'<a href="#{section_id}" class="toc-link"><span>{idx:02d}. {html.escape(label)}</span></a>')
        escaped = html.escape(text, quote=False)
        cls = callout_class(text)
        tag = "h2" if titleish(text) and idx in (1, 3, 5, 11) else ("h3" if titleish(text) else "p")
        body = f'<div class="callout {cls} animate-on-scroll"><p>{escaped}</p></div>' if cls else f"<{tag}>{escaped}</{tag}>"
        sections.append(
            f'<section id="{section_id}" class="document-section animate-on-scroll" data-section-index="{idx}">'
            f'<div class="card animate-on-scroll"><div class="section-kicker">'
            f'<span class="section-counter" data-target="{idx}">0</span><span data-ui="sourceLabel">Paragraphe source</span>'
            f"</div>{body}</div></section>"
        )
        if idx < len(paragraphs):
            sections.append('<div class="divider" aria-hidden="true"><span class="divider-line"></span><span class="divider-icon">&#9670;</span><span class="divider-line"></span></div>')

    toc = "".join(toc_items)
    lang_buttons = []
    rail_buttons = []
    for code, lang, country, flag, name, native in LANGS:
        active = " active" if code == "FR" else ""
        direction = "rtl" if code in ("AR", "HE") else "ltr"
        attrs = f'data-lang-code="{code}" data-html-lang="{lang}" data-dir="{direction}" data-lang-name="{html.escape(name)}"'
        lang_buttons.append(f'<button class="language-pill{active}" type="button" {attrs}><span class="flag">{flag}</span><strong>{html.escape(name)}</strong><em>{html.escape(native)}</em></button>')
        rail_buttons.append(f'<button class="flag-button{active}" type="button" title="{html.escape(name)}" aria-label="{html.escape(name)}" {attrs}><span>{flag}</span><small>{country}</small></button>')

    particles = "".join(f'<span class="particle p{i}"></span>' for i in range(1, 13))
    page = f'''<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Document confidentiel EKSPECTO">
  <title>EKSPECTO - Document Confidentiel</title>
  <link rel="stylesheet" href="style.css">
  <link rel="stylesheet" href="flag-language.css">
  <link rel="stylesheet" href="responsive-polish.css">
</head>
<body>
  <div id="reading-progress" aria-hidden="true"></div>
  <div id="translation-banner" hidden><span id="translation-message">&#127760; Traductions automatiques disponibles prochainement. Langue affichée : Français</span><button type="button" id="translation-close" aria-label="Fermer la bannière">&times;</button></div>
  <header id="main-header"><nav class="nav-shell" aria-label="Navigation principale"><a class="brand" href="#hero" aria-label="EKSPECTO accueil">EKSPECTO</a><div class="header-actions"><button class="toc-toggle" type="button" data-menu-open data-ui="tocButton">TOC</button><button class="lang-trigger" type="button" aria-haspopup="dialog" aria-controls="lang-modal"><span class="current-flag" aria-hidden="true">&#x1F1EB;&#x1F1F7;</span><span class="current-code">FR</span></button><button class="hamburger" type="button" aria-label="Ouvrir le menu" aria-controls="mobile-menu" aria-expanded="false" data-menu-open><span></span><span></span><span></span></button></div></nav></header>
  <aside id="flag-rail" aria-label="Sélecteur rapide de langue"><button class="flag-rail-toggle" type="button" aria-label="Afficher les langues">&#127760;</button><div class="flag-list">{''.join(rail_buttons)}</div></aside>
  <div id="mobile-menu" aria-hidden="true"><div class="mobile-backdrop" data-menu-close></div><aside class="mobile-panel" aria-label="Table des matières mobile"><div class="mobile-panel-head"><span data-ui="tocTitle">Table des matières</span><button type="button" aria-label="Fermer le menu" data-menu-close>&times;</button></div><nav class="toc-list mobile-toc">{toc}</nav></aside></div>
  <div id="lang-modal" aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="lang-title"><div class="modal-backdrop" data-lang-close></div><section class="lang-card" role="document"><button class="modal-close" type="button" aria-label="Fermer" data-lang-close>&times;</button><p class="modal-eyebrow" data-ui="languageEyebrow">Interface linguistique</p><h2 id="lang-title" data-ui="languageTitle">Choisir une langue</h2><div class="language-grid">{''.join(lang_buttons)}</div></section></div>
  <section id="hero" class="hero"><div class="particle-field" aria-hidden="true">{particles}</div><div class="hero-inner"><span class="confidential-badge" data-ui="badge">Document Confidentiel</span><h1>EKSPECTO</h1><div class="hero-line" aria-hidden="true"></div><p data-ui="heroSubtitle">Plateforme privée de prestige - présentation française</p></div></section>
  <div class="layout-wrapper"><aside id="toc-sidebar" aria-label="Table des matières"><div class="toc-card"><p data-ui="tocTitle">Table des matières</p><nav class="toc-list">{toc}</nav></div></aside><main id="main-content">{''.join(sections)}</main></div>
  <footer><div class="footer-inner"><h2>EKSPECTO</h2><p data-ui="footerNotice">Document confidentiel - usage interne uniquement</p><span class="footer-diamond">&#9670;</span><small>&copy; Copyright 2023/2026 - EKSPECTO</small></div></footer>
  <button id="back-to-top" type="button" aria-label="Retour en haut">&#8593;</button>
  <div id="google_translate_element" aria-hidden="true"></div>
  <script>
    function googleTranslateElementInit() {{
      new google.translate.TranslateElement({{
        pageLanguage: 'fr',
        includedLanguages: 'fr,en,es,ar,de,it,pt,nl,ru,zh-CN,ja,ko,tr,hi,ro,uk,pl,sv,no,da,el,id,vi,th,iw',
        autoDisplay: false
      }}, 'google_translate_element');
    }}
  </script>
  <script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
  <script src="script.js"></script>
</body>
</html>
'''
    (ROOT / "index.html").write_text(page, encoding="utf-8", newline="\n")
    print(f"Generated {len(paragraphs)} paragraphs")


if __name__ == "__main__":
    build()
