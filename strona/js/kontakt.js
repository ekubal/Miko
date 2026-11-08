// Kontakt: walidacja formularza, wysyłka do data-endpoint (albo tryb pokazowy), kopiowanie adresu.
(function () {
  "use strict";

  var form = document.getElementById("formularz");
  if (!form) return;
  var alertBox = document.getElementById("blad-wysylki");
  var submit = form.querySelector('button[type="submit"]');

  var MESSAGES = {
    imie: "Wpisz swoje imię.",
    email: "Wpisz adres e-mail, na który mamy odpowiedzieć.",
    temat: "Wybierz, czego dotyczy wiadomość.",
    wiadomosc: "Napisz kilka słów, w czym możemy pomóc.",
    zgoda: "Zaznacz zgodę, żebyśmy mogli odpowiedzieć.",
  };

  function message(el) {
    if (el.type === "email" && el.validity.typeMismatch) return "Sprawdź adres e-mail, coś się w nim nie zgadza.";
    if (el.validity.tooShort) return "Wiadomość jest za krótka. Opisz sprawę trochę dokładniej.";
    return MESSAGES[el.name] || el.validationMessage;
  }

  function show(el, text) {
    var error = document.getElementById(el.id + "-blad");
    if (error) error.textContent = text;
    if (text) el.setAttribute("aria-invalid", "true");
    else el.removeAttribute("aria-invalid");
  }

  function validate() {
    var first = null;
    form.querySelectorAll("input, select, textarea").forEach(function (el) {
      if (!el.name) return;
      var ok = el.checkValidity();
      show(el, ok ? "" : message(el));
      if (!ok && !first) first = el;
    });
    if (first) first.focus();
    return !first;
  }

  form.addEventListener("input", function (e) {
    if (e.target.getAttribute("aria-invalid") === "true" && e.target.checkValidity()) show(e.target, "");
  });
  form.addEventListener("change", function (e) {
    if (e.target.getAttribute("aria-invalid") === "true" && e.target.checkValidity()) show(e.target, "");
  });

  function success(email) {
    var box = document.createElement("section");
    box.className = "contact-success";
    box.setAttribute("role", "status");
    box.tabIndex = -1;
    box.innerHTML = '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M7 12.5l3.2 3.2L17 9"/></svg>';
    var text = document.createElement("div");
    var h = document.createElement("h2");
    h.textContent = "Dziękujemy, wiadomość dotarła do elfów";
    var p = document.createElement("p");
    p.textContent = "Odpowiemy na " + email + " w ciągu jednego dnia roboczego.";
    text.append(h, p);
    box.appendChild(text);
    form.replaceWith(box);
    box.focus();
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    alertBox.hidden = true;
    if (!validate()) return;
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = typeof v === "string" ? v.trim() : v; });
    var endpoint = form.dataset.endpoint;
    if (!endpoint) { success(data.email); return; } // tryb pokazowy
    submit.disabled = true;
    fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        success(data.email);
      })
      .catch(function (err) {
        submit.disabled = false;
        alertBox.textContent = "Nie udało się wysłać wiadomości (" + err.message + "). Spróbuj ponownie za chwilę albo napisz bezpośrednio na adres obok.";
        alertBox.hidden = false;
      });
  });

  // Kopiowanie adresu e-mail; gdy schowek jest niedostępny, zaznacza tekst do skopiowania ręcznie.
  document.querySelectorAll("[data-kopiuj]").forEach(function (button) {
    button.addEventListener("click", function () {
      var source = document.getElementById(button.dataset.kopiuj);
      var label = button.textContent;
      function selectText() {
        var range = document.createRange();
        range.selectNodeContents(source);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
      }
      var done = function () { button.textContent = "Skopiowano"; setTimeout(function () { button.textContent = label; }, 2000); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(source.textContent.trim()).then(done, selectText);
      } else selectText();
    });
  });
})();
