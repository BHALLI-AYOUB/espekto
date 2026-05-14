const header = document.getElementById('main-header');
const progress = document.getElementById('reading-progress');
const backToTop = document.getElementById('back-to-top');
const mobileMenu = document.getElementById('mobile-menu');
const hamburger = document.querySelector('.hamburger');
const langModal = document.getElementById('lang-modal');
const translationBanner = document.getElementById('translation-banner');
const translationMessage = document.getElementById('translation-message');
const flagRail = document.getElementById('flag-rail');
const tocLinks = Array.from(document.querySelectorAll('.toc-link'));
const sections = Array.from(document.querySelectorAll('.document-section'));

const uiText = {
  FR: {
    tocButton: 'TOC',
    tocTitle: 'Table des matières',
    sourceLabel: 'Paragraphe source',
    badge: 'Document Confidentiel',
    heroSubtitle: 'Plateforme privée de prestige - présentation française',
    languageEyebrow: 'Interface linguistique',
    languageTitle: 'Choisir une langue',
    footerNotice: 'Document confidentiel - usage interne uniquement',
    banner: 'Traductions automatiques disponibles prochainement. Langue affichée : '
  },
  EN: {
    tocButton: 'TOC',
    tocTitle: 'Table of contents',
    sourceLabel: 'Source paragraph',
    badge: 'Confidential Document',
    heroSubtitle: 'Private prestige platform - French presentation',
    languageEyebrow: 'Language interface',
    languageTitle: 'Choose a language',
    footerNotice: 'Confidential document - internal use only',
    banner: 'Automatic translations coming soon. Displayed language: '
  },
  ES: {
    tocButton: 'Índice',
    tocTitle: 'Tabla de contenidos',
    sourceLabel: 'Párrafo fuente',
    badge: 'Documento confidencial',
    heroSubtitle: 'Plataforma privada de prestigio - presentación francesa',
    languageEyebrow: 'Interfaz lingüística',
    languageTitle: 'Elegir un idioma',
    footerNotice: 'Documento confidencial - uso interno únicamente',
    banner: 'Traducciones automáticas disponibles próximamente. Idioma mostrado: '
  },
  AR: {
    tocButton: 'الفهرس',
    tocTitle: 'جدول المحتويات',
    sourceLabel: 'فقرة المصدر',
    badge: 'وثيقة سرية',
    heroSubtitle: 'منصة خاصة فاخرة - عرض باللغة الفرنسية',
    languageEyebrow: 'واجهة اللغة',
    languageTitle: 'اختر لغة',
    footerNotice: 'وثيقة سرية - للاستخدام الداخلي فقط',
    banner: 'ستتوفر الترجمات الآلية قريبًا. اللغة المعروضة: '
  },
  DE: {
    tocButton: 'Inhalt',
    tocTitle: 'Inhaltsverzeichnis',
    sourceLabel: 'Quellabsatz',
    badge: 'Vertrauliches Dokument',
    heroSubtitle: 'Private Prestige-Plattform - französische Präsentation',
    languageEyebrow: 'Sprachoberfläche',
    languageTitle: 'Sprache wählen',
    footerNotice: 'Vertrauliches Dokument - nur für internen Gebrauch',
    banner: 'Automatische Übersetzungen bald verfügbar. Angezeigte Sprache: '
  },
  IT: {
    tocButton: 'Indice',
    tocTitle: 'Indice',
    sourceLabel: 'Paragrafo sorgente',
    badge: 'Documento riservato',
    heroSubtitle: 'Piattaforma privata di prestigio - presentazione francese',
    languageEyebrow: 'Interfaccia lingua',
    languageTitle: 'Scegli una lingua',
    footerNotice: 'Documento riservato - solo uso interno',
    banner: 'Traduzioni automatiche presto disponibili. Lingua visualizzata: '
  },
  PT: {
    tocButton: 'Índice',
    tocTitle: 'Índice',
    sourceLabel: 'Parágrafo fonte',
    badge: 'Documento confidencial',
    heroSubtitle: 'Plataforma privada de prestígio - apresentação francesa',
    languageEyebrow: 'Interface de idioma',
    languageTitle: 'Escolher idioma',
    footerNotice: 'Documento confidencial - uso interno apenas',
    banner: 'Traduções automáticas disponíveis em breve. Idioma exibido: '
  },
  NL: {
    tocButton: 'Inhoud',
    tocTitle: 'Inhoudsopgave',
    sourceLabel: 'Bronparagraaf',
    badge: 'Vertrouwelijk document',
    heroSubtitle: 'Privé prestigeplatform - Franse presentatie',
    languageEyebrow: 'Taalinterface',
    languageTitle: 'Kies een taal',
    footerNotice: 'Vertrouwelijk document - alleen intern gebruik',
    banner: 'Automatische vertalingen binnenkort beschikbaar. Weergegeven taal: '
  },
  HE: {
    tocButton: 'תוכן',
    tocTitle: 'תוכן עניינים',
    sourceLabel: 'פסקת מקור',
    badge: 'מסמך חסוי',
    heroSubtitle: 'פלטפורמה פרטית יוקרתית - מצגת בצרפתית',
    languageEyebrow: 'ממשק שפה',
    languageTitle: 'בחר שפה',
    footerNotice: 'מסמך חסוי - לשימוש פנימי בלבד',
    banner: 'תרגומים אוטומטיים יהיו זמינים בקרוב. השפה המוצגת: '
  }
};

const fallbackText = uiText.EN;
const googleLangMap = {
  FR: 'fr',
  EN: 'en',
  ES: 'es',
  AR: 'ar',
  DE: 'de',
  IT: 'it',
  PT: 'pt',
  NL: 'nl',
  RU: 'ru',
  ZH: 'zh-CN',
  JA: 'ja',
  KO: 'ko',
  TR: 'tr',
  HI: 'hi',
  RO: 'ro',
  UK: 'uk',
  PL: 'pl',
  SV: 'sv',
  NO: 'no',
  DA: 'da',
  EL: 'el',
  ID: 'id',
  VI: 'vi',
  TH: 'th',
  HE: 'iw'
};

document.querySelectorAll('.flag-button').forEach((button) => {
  const code = (button.dataset.langCode || '').toLowerCase();
  button.innerHTML = `<span class="mini-flag flag-${code}" aria-hidden="true"></span>`;
});

const updateScrollUi = () => {
  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  const total = document.documentElement.scrollHeight - window.innerHeight;
  const percent = total > 0 ? (scrollTop / total) * 100 : 0;
  progress.style.width = `${Math.min(100, Math.max(0, percent))}%`;
  backToTop.classList.toggle('is-visible', scrollTop > 400);
  header.classList.toggle('scrolled', scrollTop > 60);
  document.body.classList.toggle('header-small', scrollTop > 60);
};

const animateCounters = (root) => {
  root.querySelectorAll('.section-counter').forEach((counter) => {
    if (counter.dataset.counted === 'true') return;
    counter.dataset.counted = 'true';
    const target = Number(counter.dataset.target || 0);
    const duration = 650;
    const start = performance.now();
    const tick = (now) => {
      const progressValue = Math.min((now - start) / duration, 1);
      counter.textContent = Math.round(progressValue * target).toString().padStart(2, '0');
      if (progressValue < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });
};

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add('is-visible');
    animateCounters(entry.target);
    revealObserver.unobserve(entry.target);
  });
}, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

document.querySelectorAll('.animate-on-scroll').forEach((element) => revealObserver.observe(element));

const activeObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    const id = entry.target.id;
    tocLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${id}`));
  });
}, { threshold: 0.18, rootMargin: '-25% 0px -60% 0px' });

sections.forEach((section) => activeObserver.observe(section));

const closeMobileMenu = () => {
  mobileMenu.classList.remove('is-open');
  mobileMenu.setAttribute('aria-hidden', 'true');
  hamburger.classList.remove('is-open');
  hamburger.setAttribute('aria-expanded', 'false');
};

const openMobileMenu = () => {
  mobileMenu.classList.add('is-open');
  mobileMenu.setAttribute('aria-hidden', 'false');
  hamburger.classList.add('is-open');
  hamburger.setAttribute('aria-expanded', 'true');
};

const closeLangModal = () => {
  langModal.classList.remove('is-open');
  langModal.setAttribute('aria-hidden', 'true');
};

const openLangModal = () => {
  langModal.classList.add('is-open');
  langModal.setAttribute('aria-hidden', 'false');
};

const setLanguage = (button) => {
  const code = button.dataset.langCode || 'FR';
  const htmlLang = button.dataset.htmlLang || 'fr';
  const direction = button.dataset.dir || 'ltr';
  const name = button.dataset.langName || 'Français';
  const copy = uiText[code] || fallbackText;
  const selectedPill = document.querySelector(`.language-pill[data-lang-code="${code}"] .flag`);

  document.documentElement.lang = htmlLang;
  document.documentElement.dir = direction;
  document.querySelectorAll('[data-ui]').forEach((element) => {
    const key = element.dataset.ui;
    if (copy[key]) element.textContent = copy[key];
  });
  document.querySelectorAll('.language-pill, .flag-button').forEach((item) => {
    item.classList.toggle('active', item.dataset.langCode === code);
  });
  document.querySelector('.current-flag').innerHTML = selectedPill ? selectedPill.innerHTML : '';
  document.querySelector('.current-code').textContent = code;
  translationMessage.textContent = `🌐 ${copy.banner}${name}`;
  translationBanner.hidden = false;
  translateWholePage(code);
  closeLangModal();
  flagRail.classList.remove('is-open');
};

const translateWholePage = (code, attempt = 0) => {
  const googleCode = googleLangMap[code] || 'fr';
  const combo = document.querySelector('.goog-te-combo');
  if (!combo) {
    if (attempt < 30) window.setTimeout(() => translateWholePage(code, attempt + 1), 250);
    return;
  }
  combo.value = googleCode;
  combo.dispatchEvent(new Event('change'));
};

document.querySelectorAll('[data-menu-open]').forEach((button) => button.addEventListener('click', openMobileMenu));
document.querySelectorAll('[data-menu-close]').forEach((button) => button.addEventListener('click', closeMobileMenu));
document.querySelector('.lang-trigger').addEventListener('click', openLangModal);
document.querySelectorAll('[data-lang-close]').forEach((button) => button.addEventListener('click', closeLangModal));
document.querySelector('.flag-rail-toggle').addEventListener('click', () => flagRail.classList.toggle('is-open'));
document.querySelectorAll('.language-pill, .flag-button').forEach((button) => button.addEventListener('click', () => setLanguage(button)));
document.getElementById('translation-close').addEventListener('click', () => { translationBanner.hidden = true; });
document.addEventListener('click', (event) => {
  if (!flagRail.contains(event.target)) flagRail.classList.remove('is-open');
});

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener('click', (event) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    const offset = header.offsetHeight + 16;
    window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - offset, behavior: 'smooth' });
    closeMobileMenu();
  });
});

backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
window.addEventListener('scroll', updateScrollUi, { passive: true });
window.addEventListener('resize', updateScrollUi);
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    closeMobileMenu();
    closeLangModal();
    flagRail.classList.remove('is-open');
  }
});
updateScrollUi();
