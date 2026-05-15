const languageSelect = document.getElementById('language-select');
const scrollRoot = document.querySelector('.page');
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

const getScrollTop = () => scrollRoot ? scrollRoot.scrollTop : window.scrollY;

const getScrollMax = () => {
  if (scrollRoot) {
    return Math.max(0, scrollRoot.scrollHeight - scrollRoot.clientHeight);
  }
  return Math.max(
    document.body.scrollHeight,
    document.documentElement.scrollHeight
  ) - window.innerHeight;
};

const setScrollTop = (top, behavior = 'smooth') => {
  if (scrollRoot) {
    scrollRoot.scrollTo({ top, behavior });
    return;
  }
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

if (scrollRoot) {
  scrollRoot.addEventListener('scroll', updateMiddlePosition, { passive: true });
} else {
  window.addEventListener('scroll', updateMiddlePosition, { passive: true });
}
window.addEventListener('resize', updateMiddlePosition);
updateMiddlePosition();
