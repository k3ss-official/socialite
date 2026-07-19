/* cinema theme runtime: scroll progress, topbar state, reveal-on-scroll,
   scrubbed photo chapters, about-image parallax, sticky CTA. No dependencies. */
(function () {
  "use strict";
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* reveal on scroll */
  var revealed = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
    revealed.forEach(function (el) { io.observe(el); });
  } else {
    revealed.forEach(function (el) { el.classList.add("is-in"); });
  }

  var bar = document.querySelector(".progress span");
  var topbar = document.querySelector("[data-topbar]");
  var hero = document.querySelector("[data-hero]");
  var stickyCta = document.querySelector("[data-sticky-cta]");
  var scrub = document.querySelector("[data-scrub]");
  var frames = scrub ? [].slice.call(scrub.querySelectorAll("[data-frame]")) : [];
  var dots = scrub ? [].slice.call(scrub.querySelectorAll(".frame-progress span")) : [];
  var parallax = document.querySelector("[data-parallax] img");
  var activeFrame = 0;

  function onScroll() {
    var y = window.scrollY;
    var vh = window.innerHeight;

    if (bar) {
      var total = document.documentElement.scrollHeight - vh;
      bar.style.width = (total > 0 ? (y / total) * 100 : 0) + "%";
    }
    if (topbar && hero) {
      topbar.classList.toggle("is-solid", y > hero.offsetHeight - 80);
    }
    if (stickyCta && hero) {
      stickyCta.classList.toggle("is-visible", y > hero.offsetHeight * 0.9);
    }
    if (scrub && frames.length) {
      var rect = scrub.getBoundingClientRect();
      var span = scrub.offsetHeight - vh;
      var progress = span > 0 ? Math.min(1, Math.max(0, -rect.top / span)) : 0;
      var idx = Math.min(frames.length - 1, Math.floor(progress * frames.length));
      if (idx !== activeFrame) {
        frames[activeFrame].classList.remove("is-active");
        if (dots[activeFrame]) dots[activeFrame].classList.remove("is-active");
        frames[idx].classList.add("is-active");
        if (dots[idx]) dots[idx].classList.add("is-active");
        activeFrame = idx;
      }
    }
    if (parallax && !reduced) {
      var pr = parallax.parentElement.getBoundingClientRect();
      if (pr.bottom > 0 && pr.top < vh) {
        var t = (pr.top + pr.height / 2 - vh / 2) / vh; /* -0.5..0.5-ish */
        parallax.style.setProperty("--py", (t * -36).toFixed(1));
      }
    }
  }

  var ticking = false;
  window.addEventListener("scroll", function () {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(function () { onScroll(); ticking = false; });
    }
  }, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();
})();
