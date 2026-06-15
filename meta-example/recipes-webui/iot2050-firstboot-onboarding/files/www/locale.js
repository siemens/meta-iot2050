(function (root) {
  const cockpit = root.cockpit || {};
  let poData = {};
  let pluralForms = function (n) { return n !== 1 ? 1 : 0; };

  cockpit.language = cockpit.language || 'en';
  cockpit.language_direction = cockpit.language_direction || 'ltr';

  cockpit.locale = function locale(po) {
    if (po === null) {
      poData = {};
      pluralForms = function (n) { return n !== 1 ? 1 : 0; };
      cockpit.language = 'en';
      cockpit.language_direction = 'ltr';
      return;
    }

    if (!po || typeof po !== 'object') {
      return;
    }

    const header = po[''] || {};
    const merged = { ...poData };

    Object.entries(po).forEach(([key, value]) => {
      if (key !== '') {
        merged[key] = value;
      }
    });

    poData = merged;

    if (typeof header['plural-forms'] === 'function') {
      pluralForms = header['plural-forms'];
    }
    if (typeof header.language === 'string' && header.language) {
      cockpit.language = header.language;
    }
    if (typeof header['language-direction'] === 'string' && header['language-direction']) {
      cockpit.language_direction = header['language-direction'];
    }
  };

  cockpit.gettext = function gettext(context, string) {
    let key = context;
    let fallback = context;

    if (arguments.length === 2) {
      key = context + '\u0004' + string;
      fallback = string;
    }

    const translated = poData[key];
    return translated && translated[1] ? translated[1] : fallback;
  };

  cockpit.ngettext = function ngettext(context, singular, plural, count) {
    let key = context;
    let singularFallback = context;
    let pluralFallback = singular;
    let amount = plural;

    if (arguments.length === 4) {
      key = context + '\u0004' + singular;
      singularFallback = singular;
      pluralFallback = plural;
      amount = count;
    }

    const translated = poData[key];
    if (translated) {
      const index = Number(pluralForms(amount)) + 1;
      if (translated[index]) {
        return translated[index];
      }
    }

    return amount === 1 ? singularFallback : pluralFallback;
  };

  cockpit.translate = function translate(target) {
    const rootNode = target || document;
    const items = rootNode.querySelectorAll ? rootNode.querySelectorAll('[translate]') : [];
    items.forEach((element) => {
      element.textContent = cockpit.gettext(element.textContent);
      element.removeAttribute('translate');
    });
  };

  root.cockpit = cockpit;
}(window));
