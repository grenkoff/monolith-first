class SiteChoice extends HTMLElement {
  connectedCallback() {
    this.querySelector('select').addEventListener('change', () => {
      this.closest('form').requestSubmit();
    });
  }
}

customElements.define('site-choice', SiteChoice);
