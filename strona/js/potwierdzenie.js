// Potwierdzenie: wpisuje numer, imiona, e-mail i kwotę w elementy z data-wartosc.
//
// Skąd biorą się dane (pierwsze, które jest dostępne):
// 1. <body data-podsumowanie="/api/zamowienia/{id}"> i ?zamowienie=<id> w adresie strony:
//    GET na ten adres, odpowiedź JSON {"nr", "imiona", "email", "kwota"}. Tak wraca rodzic po płatności.
// 2. Tryb pokazowy: podsumowanie zapisane przez formularz w sessionStorage tej karty.
// 3. Nic: zostają teksty domyślne z HTML (albo wartości wpisane przez serwer).
(function () {
  "use strict";

  var DEMO_KEY = "mikolaj-zamowienie-demo";

  function fill(data) {
    if (!data) return;
    ["nr", "imiona", "email", "kwota"].forEach(function (key) {
      if (!data[key]) return;
      document.querySelectorAll('[data-wartosc="' + key + '"]').forEach(function (el) {
        el.textContent = String(data[key]);
      });
    });
  }

  var endpoint = document.body.dataset.podsumowanie;
  var id = new URLSearchParams(window.location.search).get("zamowienie");
  if (endpoint && id) {
    fetch(endpoint.replace("{id}", encodeURIComponent(id)), { headers: { Accept: "application/json" }, credentials: "same-origin" })
      .then(function (response) { return response.ok ? response.json() : null; })
      .then(fill)
      .catch(function () { /* zostają teksty domyślne */ });
    return;
  }

  try {
    fill(JSON.parse(sessionStorage.getItem(DEMO_KEY) || "null"));
  } catch (e) { /* brak dostępu do sessionStorage: teksty domyślne */ }
})();
