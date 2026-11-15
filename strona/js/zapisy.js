// Strona przed startem: formularz zapisu po kod rabatowy.
//
// Sprawdza e-mail i zgodę, wysyła zapis i pokazuje ekran „Sprawdź skrzynkę”.
// data-endpoint na formularzu: adres, który przyjmuje POST z JSON-em
// {"email", "zgoda", "zgoda_tresc", "zrodlo"} i odpowiada kodem 2xx.
// Puste data-endpoint = tryb pokazowy: nic nie wysyłamy, od razu pokazujemy potwierdzenie.
(function () {
  "use strict";

  var form = document.getElementById("zapis-formularz");
  if (!form) return;

  var done = document.getElementById("zapis-wyslano");
  var email = document.getElementById("email-zapis");
  var consent = document.getElementById("zgoda-zapis");
  var consentText = document.getElementById("zgoda-zapis-tresc");
  var alertBox = document.getElementById("zapis-alert");
  var trap = form.querySelector('[name="strona_www"]');
  var submitButton = form.querySelector('button[type="submit"]');
  var sending = false;

  var MESSAGES = {
    emailPusty: "Wpisz adres e-mail.",
    emailZly: "Wpisz adres e-mail w formie nazwa@domena.pl.",
    zgoda: "Zaznacz zgodę, żebyśmy mogli wysłać Ci kod.",
    wysylka: "Nie udało się zapisać adresu. Spróbuj ponownie za chwilę. Jeśli problem się powtórzy, napisz do nas.",
  };

  function emailValue() {
    return email.value.trim();
  }

  function emailMessage() {
    var value = emailValue();
    if (!value) return MESSAGES.emailPusty;
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)) return MESSAGES.emailZly;
    return "";
  }

  function showError(input, message) {
    var error = document.getElementById(input.getAttribute("aria-describedby"));
    if (error) error.textContent = message;
    if (message) input.setAttribute("aria-invalid", "true");
    else input.removeAttribute("aria-invalid");
  }

  // Pokazuje komunikaty i zwraca pierwsze błędne pole (albo null).
  function validate() {
    var emailError = emailMessage();
    var consentError = consent.checked ? "" : MESSAGES.zgoda;
    showError(email, emailError);
    showError(consent, consentError);
    if (emailError) return email;
    if (consentError) return consent;
    return null;
  }

  function showAlert(message) {
    alertBox.textContent = message;
    alertBox.hidden = !message;
  }

  function setBusy(busy) {
    sending = busy;
    submitButton.disabled = busy;
    submitButton.setAttribute("aria-busy", busy ? "true" : "false");
  }

  function showDone(address) {
    done.querySelector("[data-zapis-adres]").textContent = address;
    form.hidden = true;
    done.hidden = false;
    done.querySelector(".signup__title").focus();
  }

  function send(endpoint, address) {
    return fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({
        email: address,
        zgoda: true,
        // Treść zgody, którą widział rodzic: serwer zapisuje ją razem z datą jako dowód zgody.
        zgoda_tresc: consentText.textContent.replace(/\s+/g, " ").trim(),
        zrodlo: "zapisy",
      }),
    }).then(function (response) {
      if (!response.ok) throw new Error("HTTP " + response.status);
    });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (sending) return;
    showAlert("");
    var invalid = validate();
    if (invalid) { invalid.focus(); return; }

    var address = emailValue();
    // Wypełnione ukryte pole = automat. Udajemy sukces i nic nie wysyłamy.
    if (trap && trap.value) { showDone(address); return; }

    var endpoint = form.dataset.endpoint;
    if (!endpoint) { showDone(address); return; }

    setBusy(true);
    send(endpoint, address)
      .then(function () { setBusy(false); showDone(address); })
      .catch(function () { setBusy(false); showAlert(MESSAGES.wysylka); });
  });

  // Po poprawieniu pola komunikat znika od razu, bez ponownego klikania przycisku.
  email.addEventListener("input", function () {
    if (email.getAttribute("aria-invalid") === "true" && !emailMessage()) showError(email, "");
  });
  consent.addEventListener("change", function () {
    if (consent.checked) showError(consent, "");
  });

  done.querySelector("[data-zapis-ponownie]").addEventListener("click", function () {
    form.reset();
    showError(email, "");
    showError(consent, "");
    showAlert("");
    done.hidden = true;
    form.hidden = false;
    email.focus();
  });
})();
