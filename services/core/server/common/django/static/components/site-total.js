const CENTS = 100;

const MONEY = new Intl.NumberFormat('en', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  useGrouping: false,
});

class SiteTotal extends HTMLElement {
  connectedCallback() {
    const quantity = this.querySelector('input[name="quantity"]');
    const total = this.querySelector('output[name="total"]');
    const price = Number(this.getAttribute('price-cents'));
    const show = () => {
      total.value = quantity.checkValidity()
        ? MONEY.format((price * Number(quantity.value)) / CENTS)
        : '—';
    };
    quantity.addEventListener('input', show);
    show();
  }
}

customElements.define('site-total', SiteTotal);
