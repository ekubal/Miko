// Strona główna: film przykładowy w ramce prezentu.
// Plik filmu i kadr podajesz w atrybutach data-video i data-poster elementu .video.
(function () {
  "use strict";

  document.querySelectorAll(".video[data-video]").forEach(function (box) {
    var button = box.querySelector(".video__play");
    var caption = box.querySelector(".video__caption");
    var poster = box.getAttribute("data-poster");

    // Kadr jako tło, jeśli plik istnieje (brak pliku = ciemne tło z projektu).
    if (poster) {
      var probe = new Image();
      probe.onload = function () { box.style.backgroundImage = "url('" + poster + "')"; };
      probe.src = poster;
    }

    if (!button) return;
    button.addEventListener("click", function () {
      var video = document.createElement("video");
      video.src = box.getAttribute("data-video");
      video.controls = true;
      video.playsInline = true;
      video.preload = "auto";
      if (poster) video.poster = poster;
      video.addEventListener("error", function () {
        video.remove();
        button.hidden = false;
        if (caption) {
          caption.hidden = false;
          caption.textContent = "Film przykładowy pojawi się tu wkrótce.";
        }
      });
      button.hidden = true;
      if (caption) caption.hidden = true;
      box.appendChild(video);
      var playing = video.play();
      if (playing && playing.catch) playing.catch(function () { /* autoplay zablokowany: zostają kontrolki */ });
      video.focus();
    });
  });
})();
