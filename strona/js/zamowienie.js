// Formularz zamówienia: kroki, rodzeństwo, walidacja, podsumowanie i wysyłka.
//
// Kroki: dla każdego dziecka "podstawowe" i "wiadomosc", na końcu "dane" (e-mail, termin, zgody).
// Dane dziecka mają te same nazwy co plik zamówienia generatora (examples/zamowienie_kasia.json):
// imie, zwrot, plec, wiek, osiagniecie, zainteresowania, do_poprawy, prezent, prezent_kupiony.
(function () {
  "use strict";

  var form = document.getElementById("zamowienie");
  if (!form) return;

  var BASE_PRICE = Number(form.dataset.cenaBazowa) || 49;
  var SIBLING_PRICE = Number(form.dataset.cenaRodzenstwo) || 15;
  var MAX_CHILDREN = Number(form.dataset.maksDzieci) || 4;
  var MAX_MB = Number(form.dataset.maksMb) || 20;
  var DEMO_KEY = "mikolaj-zamowienie-demo";

  var list = document.getElementById("dzieci");
  var template = document.getElementById("szablon-dziecka");
  var finalStep = form.querySelector('[data-krok="dane"]');
  var progressItems = document.querySelectorAll("#postep li");
  var summaryList = document.getElementById("lista-dzieci");
  var alertBox = document.getElementById("blad-wysylki");
  var submitButton = form.querySelector('button[type="submit"]');

  var pos = 0;
  var dirty = false;
  var submitting = false;

  var MESSAGES = {
    imie: "Wpisz imię dziecka.",
    zwrot: "Wpisz, jak Mikołaj ma się zwracać do dziecka.",
    plec: "Zaznacz jedną z odpowiedzi.",
    wiek: "Wybierz wiek dziecka.",
    zdjecie: "Dodaj zdjęcie dziecka (JPG lub PNG).",
    osiagniecie: "Napisz, co udało się dziecku w tym roku.",
    zainteresowania: "Napisz, co dziecko lubi.",
    prezent_kupiony: "Zaznacz „tak” albo „nie”.",
    email: "Wpisz adres e-mail.",
    termin: "Wybierz datę.",
    zgoda: "Zaznacz wszystkie zgody, żeby przejść do płatności.",
  };

  // --- dzieci ----------------------------------------------------------------------

  function groups() {
    return Array.prototype.slice.call(list.querySelectorAll("[data-dziecko]"));
  }

  function steps() {
    var out = [];
    groups().forEach(function (group) {
      out.push(group.querySelector('[data-krok="podstawowe"]'), group.querySelector('[data-krok="wiadomosc"]'));
    });
    out.push(finalStep);
    return out;
  }

  function field(group, name) {
    return group.querySelector('[data-pole="' + name + '"]');
  }

  function value(group, name) {
    var checked = group.querySelector('[data-pole="' + name + '"]:checked');
    if (checked) return checked.value;
    var el = field(group, name);
    return el && el.type !== "radio" ? el.value.trim() : "";
  }

  function addChild() {
    var fragment = template.content.cloneNode(true);
    var group = fragment.querySelector("[data-dziecko]");
    list.appendChild(fragment);
    renumber();
    return group;
  }

  // Nazwy pól dzieci[N][pole], identyfikatory i powiązania etykiet po każdej zmianie liczby dzieci.
  function renumber() {
    groups().forEach(function (group, i) {
      var n = i + 1;
      group.querySelectorAll("[data-pole]").forEach(function (el) {
        var name = el.dataset.pole;
        el.name = "dzieci[" + i + "][" + name + "]";
        if (el.type === "radio") return;
        el.id = name + "-" + n;
        var ids = [];
        var hint = group.querySelector('[data-opis="' + name + '"]');
        var error = group.querySelector('[data-blad="' + name + '"]');
        if (hint) { hint.id = name + "-opis-" + n; ids.push(hint.id); }
        if (error) { error.id = name + "-blad-" + n; ids.push(error.id); }
        if (ids.length) el.setAttribute("aria-describedby", ids.join(" "));
      });
      group.querySelectorAll("[data-grupa]").forEach(function (set) {
        var name = set.dataset.grupa;
        var ids = [];
        var hint = group.querySelector('[data-opis="' + name + '"]');
        var error = group.querySelector('[data-blad="' + name + '"]');
        if (hint) { hint.id = name + "-opis-" + n; ids.push(hint.id); }
        if (error) { error.id = name + "-blad-" + n; ids.push(error.id); }
        set.setAttribute("aria-describedby", ids.join(" "));
      });
      group.querySelectorAll("[data-for]").forEach(function (label) {
        label.htmlFor = label.dataset.for + "-" + n;
      });
      group.querySelectorAll("[data-numer]").forEach(function (el) { el.textContent = String(n); });
      group.querySelectorAll("[data-tylko-rodzenstwo]").forEach(function (el) { el.hidden = i === 0; });
    });
    refresh();
  }

  function childLabel(group, i) {
    return value(group, "imie") || "Dziecko " + (i + 1);
  }

  function joinNames(names) {
    if (names.length < 2) return names[0] || "";
    return names.slice(0, -1).join(", ") + " i " + names[names.length - 1];
  }

  function total() {
    return BASE_PRICE + (groups().length - 1) * SIBLING_PRICE;
  }

  // Podsumowanie, ceny, podpisy kroków i oferta rodzeństwa.
  function refresh() {
    var all = groups();
    var count = all.length;
    var extra = count - 1;

    summaryList.textContent = "";
    all.forEach(function (group, i) {
      var item = document.createElement("li");
      var label = document.createElement("span");
      label.className = "summary__child";
      label.innerHTML = '<svg class="icon icon--16" style="fill: var(--accent)" aria-hidden="true"><use href="#i-star"/></svg>';
      label.appendChild(document.createTextNode(childLabel(group, i)));
      var edit = document.createElement("button");
      edit.type = "button";
      edit.className = "summary__edit";
      edit.dataset.akcja = "popraw";
      edit.dataset.krok = String(i * 2);
      edit.textContent = "Popraw";
      edit.setAttribute("aria-label", "Popraw dane: " + childLabel(group, i));
      item.append(label, edit);
      summaryList.appendChild(item);

      var caption = group.querySelector("[data-podpis-dziecka]");
      var name = value(group, "imie");
      caption.textContent = i > 0 ? "Rodzeństwo · " + (name || "dziecko " + (i + 1)) : name;
      caption.hidden = !caption.textContent;

      group.querySelector("[data-etykieta-dalej]").textContent =
        i === count - 1 ? "Dalej: Twoje dane" : "Dalej: kolejne dziecko";
      group.querySelector("[data-oferta-rodzenstwa]").hidden = !(i === count - 1 && count < MAX_CHILDREN);
    });

    form.querySelector("[data-rodzenstwo]").hidden = extra === 0;
    form.querySelector("[data-rodzenstwo-opis]").textContent = extra + " × " + SIBLING_PRICE + " zł";
    form.querySelector("[data-rodzenstwo-cena]").textContent = extra * SIBLING_PRICE + " zł";
    form.querySelectorAll("[data-suma]").forEach(function (el) { el.textContent = total() + " zł"; });
  }

  // --- kroki -------------------------------------------------------------------------

  function go(target, focus) {
    var all = steps();
    pos = Math.max(0, Math.min(target, all.length - 1));
    all.forEach(function (step, i) { step.hidden = i !== pos; });

    var stage = pos === all.length - 1 ? 2 : pos % 2;
    progressItems.forEach(function (item, i) {
      item.classList.toggle("is-done", i < stage);
      item.classList.toggle("is-current", i === stage);
      if (i === stage) item.setAttribute("aria-current", "step");
      else item.removeAttribute("aria-current");
      item.querySelector(".progress__dot").textContent = i < stage ? "✓" : String(i + 1);
    });

    if (focus !== false) {
      window.scrollTo({ top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
      var heading = all[pos].querySelector(".panel__title");
      if (heading) heading.focus({ preventScroll: true });
    }
  }

  function next() {
    if (!validateStep(steps()[pos], true)) return;
    go(pos + 1);
  }

  function addSibling() {
    if (groups().length >= MAX_CHILDREN) return;
    if (!validateStep(steps()[pos], true)) return;
    addChild();
    go((groups().length - 1) * 2);
  }

  function removeChild(group) {
    var index = groups().indexOf(group);
    if (index <= 0) return;
    group.remove();
    renumber();
    go(index * 2 - 1);
  }

  // --- walidacja ---------------------------------------------------------------------

  function errorFor(el) {
    var scope = el.closest(".field, .choice-group, .consents");
    return scope ? scope.querySelector(".field__error") : null;
  }

  function messageFor(el) {
    if (el.validity.customError) return el.validationMessage;
    if (el.type === "email" && el.validity.typeMismatch) return "Sprawdź adres e-mail, coś się w nim nie zgadza.";
    if (el.type === "date" && el.validity.rangeUnderflow) return "Wybierz dzisiejszą albo późniejszą datę.";
    return MESSAGES[el.dataset.pole] || el.validationMessage;
  }

  function showError(el, message) {
    var error = errorFor(el);
    if (error) error.textContent = message || "";
    var targets = el.type === "radio" || el.type === "checkbox"
      ? el.closest(".choice-group, .consents").querySelectorAll("input")
      : [el];
    Array.prototype.forEach.call(targets, function (target) {
      if (message) target.setAttribute("aria-invalid", "true");
      else target.removeAttribute("aria-invalid");
    });
    if (el.type === "file") {
      var zone = el.nextElementSibling;
      if (zone) zone.classList.toggle("is-invalid", Boolean(message));
    }
  }

  // Sprawdza pola kroku; przy show=true pokazuje komunikaty i ustawia fokus na pierwszym błędzie.
  function validateStep(step, show) {
    var firstInvalid = null;
    var seenGroups = {};
    step.querySelectorAll("input, select, textarea").forEach(function (el) {
      if (el.disabled || !el.dataset.pole) return;
      if (el.type === "radio" || el.type === "checkbox") {
        var key = el.type === "radio" ? el.name : "zgody";
        if (seenGroups[key]) return;
        seenGroups[key] = true;
        var members = el.type === "radio"
          ? step.querySelectorAll('input[name="' + el.name + '"]')
          : step.querySelectorAll('input[type="checkbox"][required]');
        var ok = Array.prototype.some.call(members, function (m) { return m.checked; });
        if (el.type === "checkbox") ok = Array.prototype.every.call(members, function (m) { return m.checked; });
        if (show) showError(el, ok ? "" : MESSAGES[el.dataset.pole]);
        if (!ok && !firstInvalid) {
          firstInvalid = Array.prototype.find.call(members, function (m) { return !m.checked; }) || el;
        }
        return;
      }
      var valid = el.checkValidity();
      if (show) showError(el, valid ? "" : messageFor(el));
      if (!valid && !firstInvalid) firstInvalid = el;
    });
    if (firstInvalid && show) firstInvalid.focus();
    return !firstInvalid;
  }

  // --- zdjęcie -----------------------------------------------------------------------

  function setPhoto(input) {
    var file = input.files && input.files[0];
    var zone = input.nextElementSibling;
    var preview = zone.querySelector("[data-podglad]");
    var nameEl = zone.querySelector("[data-plik]");
    var extraEl = zone.querySelector("[data-plik-dopisek]");
    input.setCustomValidity("");
    if (file && !/^image\/(jpeg|png)$/.test(file.type)) {
      input.setCustomValidity("To nie jest zdjęcie JPG ani PNG. Wybierz inny plik.");
    } else if (file && file.size > MAX_MB * 1024 * 1024) {
      input.setCustomValidity("Zdjęcie jest za duże (największe: " + MAX_MB + " MB). Wybierz mniejsze.");
    }

    if (preview.dataset.url) URL.revokeObjectURL(preview.dataset.url);
    if (!preview.dataset.ikona) preview.dataset.ikona = preview.innerHTML;
    if (file && input.validity.valid) {
      var url = URL.createObjectURL(file);
      preview.dataset.url = url;
      preview.innerHTML = "";
      var img = document.createElement("img");
      img.src = url;
      img.alt = "";
      preview.appendChild(img);
      nameEl.textContent = file.name;
      extraEl.textContent = "· kliknij, żeby zmienić";
    } else {
      delete preview.dataset.url;
      preview.innerHTML = preview.dataset.ikona;
      nameEl.textContent = "Wybierz zdjęcie";
      extraEl.textContent = "albo przeciągnij je tutaj";
    }
    if (file || zone.classList.contains("is-invalid")) showError(input, input.validity.valid ? "" : messageFor(input));
  }

  form.addEventListener("dragover", function (event) {
    var zone = event.target.closest && event.target.closest(".dropzone");
    if (!zone) return;
    event.preventDefault();
    zone.classList.add("is-dragover");
  });
  form.addEventListener("dragleave", function (event) {
    var zone = event.target.closest && event.target.closest(".dropzone");
    if (zone) zone.classList.remove("is-dragover");
  });
  form.addEventListener("drop", function (event) {
    var zone = event.target.closest && event.target.closest(".dropzone");
    if (!zone) return;
    event.preventDefault();
    zone.classList.remove("is-dragover");
    var input = zone.previousElementSibling;
    if (event.dataTransfer && event.dataTransfer.files.length) {
      input.files = event.dataTransfer.files;
      input.dispatchEvent(new Event("change", { bubbles: true }));
    }
  });

  // --- zdarzenia ------------------------------------------------------------------------

  form.addEventListener("click", function (event) {
    var button = event.target.closest("[data-akcja]");
    if (!button) return;
    var action = button.dataset.akcja;
    if (action === "dalej") next();
    else if (action === "wstecz") go(pos - 1);
    else if (action === "dodaj") addSibling();
    else if (action === "usun") removeChild(button.closest("[data-dziecko]"));
    else if (action === "popraw") go(Number(button.dataset.krok));
  });

  form.addEventListener("input", function (event) {
    dirty = true;
    var el = event.target;
    if (el.dataset.pole === "imie") refresh();
    if (el.getAttribute("aria-invalid") === "true" && el.type !== "file") {
      if (el.type === "radio" || el.type === "checkbox") return;
      if (el.checkValidity()) showError(el, "");
    }
  });

  form.addEventListener("change", function (event) {
    dirty = true;
    var el = event.target;
    if (el.type === "file") { setPhoto(el); return; }
    if (el.type === "radio" && el.getAttribute("aria-invalid") === "true") showError(el, "");
    if (el.type === "checkbox" && el.getAttribute("aria-invalid") === "true") {
      var all = form.querySelectorAll('.consents input[type="checkbox"][required]');
      if (Array.prototype.every.call(all, function (c) { return c.checked; })) showError(el, "");
    }
    if (el.tagName === "SELECT" && el.checkValidity()) showError(el, "");
  });

  // Enter w polu tekstowym przechodzi do następnego kroku zamiast wysyłać formularz.
  form.addEventListener("keydown", function (event) {
    if (event.key !== "Enter" || event.target.tagName !== "INPUT") return;
    if (event.target.type === "submit" || event.target.type === "button") return;
    if (pos < steps().length - 1) {
      event.preventDefault();
      next();
    }
  });

  window.addEventListener("beforeunload", function (event) {
    if (!dirty || submitting) return;
    event.preventDefault();
    event.returnValue = "";
  });

  // --- wysyłka -----------------------------------------------------------------------

  function collect() {
    return {
      dzieci: groups().map(function (group, i) {
        return {
          imie: value(group, "imie"),
          zwrot: value(group, "zwrot"),
          plec: value(group, "plec"),
          wiek: value(group, "wiek"),
          zdjecie: "zdjecie_" + i,
          osiagniecie: value(group, "osiagniecie"),
          zainteresowania: value(group, "zainteresowania"),
          do_poprawy: value(group, "do_poprawy"),
          prezent: value(group, "prezent"),
          prezent_kupiony: value(group, "prezent_kupiony") === "tak",
        };
      }),
      email: document.getElementById("email").value.trim(),
      termin: document.getElementById("termin").value,
      zgody: { regulamin: true, dane_dziecka: true, ai: true, realizacja: true },
      kwota_zl: total(),
    };
  }

  function setBusy(busy) {
    submitting = busy;
    submitButton.disabled = busy;
    submitButton.setAttribute("aria-busy", busy ? "true" : "false");
  }

  function showAlert(message) {
    alertBox.textContent = message;
    alertBox.hidden = !message;
  }

  function sendToServer(endpoint, order) {
    var data = new FormData();
    data.append("zamowienie", JSON.stringify(order));
    groups().forEach(function (group, i) {
      var file = field(group, "zdjecie").files[0];
      data.append("zdjecie_" + i, file, file.name);
    });
    return fetch(endpoint, {
      method: "POST",
      body: data,
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    }).then(function (response) {
      return response.json().catch(function () { return {}; }).then(function (body) {
        if (!response.ok) throw new Error(body.blad || "HTTP " + response.status);
        var url = body.platnosc_url || body.redirect;
        if (!url) throw new Error("serwer nie podał adresu płatności");
        return url;
      });
    });
  }

  // Tryb pokazowy (bez data-endpoint): zapisuje podsumowanie w tej karcie przeglądarki
  // i przechodzi do potwierdzenia. Zdjęcia nigdzie nie są wysyłane.
  function demo(order) {
    var summary = {
      nr: "POKAZ-" + Math.floor(1000 + Math.random() * 9000),
      imiona: joinNames(order.dzieci.map(function (c) { return c.imie; })),
      email: order.email,
      kwota: order.kwota_zl + " zł",
    };
    try { sessionStorage.setItem(DEMO_KEY, JSON.stringify(summary)); } catch (e) { /* prywatne okno: bez danych */ }
    window.location.assign("potwierdzenie.html");
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (submitting) return;
    showAlert("");
    var all = steps();
    for (var i = 0; i < all.length; i++) {
      if (!validateStep(all[i], false)) {
        go(i, true);
        validateStep(all[i], true);
        return;
      }
    }
    var order = collect();
    var endpoint = form.dataset.endpoint;
    setBusy(true);
    if (!endpoint) { demo(order); return; }
    sendToServer(endpoint, order)
      .then(function (url) { window.location.assign(url); })
      .catch(function (error) {
        setBusy(false);
        showAlert("Nie udało się wysłać zamówienia (" + error.message + "). Spróbuj ponownie za chwilę. " +
          "Jeśli problem się powtórzy, napisz do nas, a pomożemy.");
      });
  });

  // --- start -----------------------------------------------------------------------------

  var dateInput = document.getElementById("termin");
  var today = new Date();
  var pad = function (n) { return String(n).padStart(2, "0"); };
  dateInput.min = today.getFullYear() + "-" + pad(today.getMonth() + 1) + "-" + pad(today.getDate());

  addChild();
  go(0, false);
})();
