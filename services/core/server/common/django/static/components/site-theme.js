const STORAGE_KEY = 'site-theme';

class SiteTheme extends HTMLElement {
  connectedCallback() {
    const select = this.querySelector('select');
    const saved = this.#saved();
    if (saved && [...select.options].some((option) => option.value === saved)) {
      select.value = saved;
      this.#apply(saved);
    }
    select.addEventListener('change', () => {
      this.#apply(select.value);
      this.#save(select.value);
    });
    this.hidden = false;
  }

  #apply(theme) {
    const root = document.documentElement;
    if (document.startViewTransition) {
      document.startViewTransition(() => {
        root.dataset.theme = theme;
      });
    } else {
      root.dataset.theme = theme;
    }
  }

  #saved() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch {
      return '';
    }
  }

  #save(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      this.dataset.unsaved = theme;
    }
  }
}

customElements.define('site-theme', SiteTheme);
