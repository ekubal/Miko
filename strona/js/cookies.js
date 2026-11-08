// Zgoda na pliki cookies: baner przy pierwszej wizycie, okno ustawień, zapis wyboru.
//
// Dołącz na każdej stronie: <script src="js/cookies.js" defer></script>
// Skrypty opcjonalne wstawiaj jako nieaktywne i oznacz kategorią, np.:
//   <script type="text/plain" data-zgoda="reklamowe" data-src="https://connect.facebook.net/..."></script>
//   <script type="text/plain" data-zgoda="analityczne">/* kod narzędzia */</script>
// Skrypt uruchomi je dopiero po zgodzie na daną kategorię. Bez zgody nic się nie ładuje.
// Przycisk lub link z atrybutem data-cookies-ustawienia otwiera okno ustawień (np. w stopce).
(function () {
  "use strict";

  var KEY = "mikolaj-zgody-cookies";
  var VERSION = 1; // podnieś, gdy zmienią się kategorie albo narzędzia: baner pokaże się ponownie
  var CATEGORIES = [
    { id: "niezbedne", label: "Niezbędne", locked: true,
      text: "Zapamiętują postęp w formularzu zamówienia i Twój wybór dotyczący cookies.",
      tools: "Strona i operator płatności" },
    { id: "analityczne", label: "Analityczne",
      text: "Pomagają nam sprawdzić, które części strony są niejasne, np. gdzie rodzice przerywają zamówienie.",
      tools: "[NARZĘDZIE ANALITYCZNE]" },
    { id: "reklamowe", label: "Reklamowe",
      text: "Pozwalają sprawdzić, które reklamy prowadzą do zamówień, i pokazywać reklamy osobom, które już nas odwiedziły.",
      tools: "Meta Pixel, Google Ads" },
  ];

  function read() {
    try {
      var data = JSON.parse(localStorage.getItem(KEY) || "null");
      return data && data.v === VERSION ? data : null;
    } catch (e) { return null; }
  }

  function save(choices) {
    var data = { v: VERSION, data: new Date().toISOString(), zgody: choices };
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) { /* bez zapisu: baner wróci przy kolejnej wizycie */ }
    apply(choices);
    document.dispatchEvent(new CustomEvent("zgody-cookies", { detail: choices }));
  }

  // Uruchamia nieaktywne skrypty z kategorii, na które jest zgoda (każdy tylko raz).
  function apply(choices) {
    document.querySelectorAll('script[type="text/plain"][data-zgoda]').forEach(function (old) {
      if (!choices[old.dataset.zgoda] || old.dataset.uruchomiony) return;
      old.dataset.uruchomiony = "tak";
      var script = document.createElement("script");
      if (old.dataset.src) { script.src = old.dataset.src; script.async = true; }
      else script.textContent = old.textContent;
      old.after(script);
    });
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  var banner, dialog, lastFocus;

  function choices(all) {
    var out = {};
    CATEGORIES.forEach(function (c) { out[c.id] = c.locked ? true : all; });
    return out;
  }

  function closeBanner() { if (banner) { banner.remove(); banner = null; } }

  function buildBanner() {
    var privacy = el("a", { href: "polityka-prywatnosci.html", text: "Polityka prywatności" });
    banner = el("section", { class: "cookie-banner", role: "region", "aria-labelledby": "cookie-tytul", "aria-describedby": "cookie-opis" }, [
      el("div", { class: "cookie-banner__text" }, [
        el("h2", { id: "cookie-tytul", text: "Pierniczki dla elfów, czyli pliki cookies" }),
        el("p", { id: "cookie-opis" }, [
          document.createTextNode("Używamy niezbędnych plików cookies, żeby strona i zamówienie działały. Za Twoją zgodą użyjemy też cookies analitycznych i reklamowych, żeby sprawdzać, które reklamy prowadzą rodziców do nas. Zgodę możesz zmienić w każdej chwili w stopce strony. "),
          privacy,
        ]),
      ]),
      el("div", { class: "cookie-banner__actions" }, [
        el("button", { type: "button", class: "btn btn--outline cookie-btn", "data-akcja": "ustawienia", text: "Ustawienia" }),
        el("button", { type: "button", class: "btn cookie-btn cookie-btn--dark", "data-akcja": "odrzuc", text: "Odrzuć opcjonalne" }),
        el("button", { type: "button", class: "btn cookie-btn cookie-btn--dark", "data-akcja": "akceptuj", text: "Akceptuję wszystkie" }),
      ]),
    ]);
    banner.addEventListener("click", function (e) {
      var action = e.target.dataset && e.target.dataset.akcja;
      if (action === "akceptuj") { save(choices(true)); closeBanner(); }
      else if (action === "odrzuc") { save(choices(false)); closeBanner(); }
      else if (action === "ustawienia") openDialog();
    });
    document.body.appendChild(banner);
  }

  function buildDialog() {
    var current = (read() || {}).zgody || {};
    var rows = CATEGORIES.map(function (c) {
      var control;
      if (c.locked) {
        control = el("span", { class: "cookie-tag", text: "Zawsze włączone" });
      } else {
        control = el("button", { type: "button", class: "cookie-switch", role: "switch", "aria-checked": current[c.id] ? "true" : "false", "aria-label": c.label, "data-kategoria": c.id }, [el("span")]);
        control.addEventListener("click", function () {
          control.setAttribute("aria-checked", control.getAttribute("aria-checked") === "true" ? "false" : "true");
        });
      }
      return el("div", { class: "cookie-row" }, [
        el("div", {}, [
          el("p", { class: "cookie-row__title", text: c.label }),
          el("p", { class: "cookie-row__text", text: c.text }),
          el("p", { class: "cookie-row__tools", text: c.tools }),
        ]),
        control,
      ]);
    });
    var close = el("button", { type: "button", class: "cookie-close", "aria-label": "Zamknij", text: "×" });
    var saveBtn = el("button", { type: "button", class: "btn btn--outline cookie-btn", text: "Zapisz wybór" });
    var allBtn = el("button", { type: "button", class: "btn cookie-btn cookie-btn--dark", text: "Akceptuję wszystkie" });
    var box = el("div", { class: "cookie-dialog__box", role: "dialog", "aria-modal": "true", "aria-labelledby": "cookie-ust-tytul" }, [
      el("div", { class: "cookie-dialog__head" }, [el("h2", { id: "cookie-ust-tytul", text: "Ustawienia cookies" }), close]),
      el("p", { class: "cookie-row__text", text: "Wybierz, na co się zgadzasz. Bez zgody strona i zamówienie działają tak samo." }),
    ].concat(rows, [el("div", { class: "cookie-dialog__actions" }, [saveBtn, allBtn])]));
    dialog = el("div", { class: "cookie-dialog" }, [box]);

    close.addEventListener("click", closeDialog);
    dialog.addEventListener("click", function (e) { if (e.target === dialog) closeDialog(); });
    saveBtn.addEventListener("click", function () {
      var picked = choices(false);
      dialog.querySelectorAll("[data-kategoria]").forEach(function (s) { picked[s.dataset.kategoria] = s.getAttribute("aria-checked") === "true"; });
      save(picked); closeDialog(); closeBanner();
    });
    allBtn.addEventListener("click", function () { save(choices(true)); closeDialog(); closeBanner(); });
    dialog.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { closeDialog(); return; }
      if (e.key !== "Tab") return;
      var focusable = box.querySelectorAll("button, a[href]");
      var first = focusable[0], last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    document.body.appendChild(dialog);
    return close;
  }

  function openDialog() {
    lastFocus = document.activeElement;
    if (dialog) dialog.remove();
    var first = buildDialog();
    document.documentElement.classList.add("cookie-lock");
    first.focus();
  }

  function closeDialog() {
    if (!dialog) return;
    dialog.remove(); dialog = null;
    document.documentElement.classList.remove("cookie-lock");
    if (lastFocus && document.contains(lastFocus)) lastFocus.focus();
  }

  document.addEventListener("click", function (e) {
    var trigger = e.target.closest && e.target.closest("[data-cookies-ustawienia]");
    if (!trigger) return;
    e.preventDefault();
    openDialog();
  });

  // Dla innych skryptów: window.zgodyCookies() zwraca np. {niezbedne: true, analityczne: false, reklamowe: false}.
  window.zgodyCookies = function () { return (read() || {}).zgody || choices(false); };

  var stored = read();
  if (stored) apply(stored.zgody);
  else buildBanner();
})();
