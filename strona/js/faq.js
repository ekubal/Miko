// Pytania rodziców: wyszukiwanie w pytaniach i odpowiedziach, otwieranie pytania z adresu (#).
(function () {
  "use strict";

  var input = document.getElementById("szukaj");
  var status = document.getElementById("wynik");
  var empty = document.querySelector("[data-brak]");
  var groups = Array.prototype.slice.call(document.querySelectorAll("[data-grupa]"));
  if (!input) return;

  // Bez polskich znaków i wielkości liter: "zdjecie" znajduje "Zdjęcie".
  function normalize(text) {
    return text.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ł/g, "l");
  }

  groups.forEach(function (group) {
    group.querySelectorAll("details").forEach(function (item) {
      item.dataset.tekst = normalize(item.textContent);
    });
  });

  function filter() {
    var words = normalize(input.value).split(/\s+/).filter(Boolean);
    var found = 0;
    groups.forEach(function (group) {
      var visible = 0;
      group.querySelectorAll("details").forEach(function (item) {
        var match = words.every(function (w) { return item.dataset.tekst.indexOf(w) !== -1; });
        item.hidden = !match;
        if (words.length) item.open = match;
        if (match) visible++;
      });
      group.hidden = visible === 0;
      found += visible;
    });
    if (!words.length) {
      groups.forEach(function (g) { g.querySelectorAll("details").forEach(function (d) { d.open = false; }); });
    }
    empty.hidden = found > 0;
    status.textContent = words.length ? "Znalezione odpowiedzi: " + found : "";
  }

  input.addEventListener("input", filter);
})();
