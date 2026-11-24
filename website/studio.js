const root = document.documentElement;
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function setUpLens(lens) {
  const tabs = [...lens.querySelectorAll('[role="tab"]')];
  const panels = tabs.map(tab => document.getElementById(tab.getAttribute("aria-controls")));

  function select(tab, moveFocus = false) {
    for (const [index, item] of tabs.entries()) {
      const active = item === tab;
      item.setAttribute("aria-selected", String(active));
      item.tabIndex = active ? 0 : -1;
      panels[index].hidden = !active;
    }
    if (moveFocus) tab.focus();
  }

  for (const [index, tab] of tabs.entries()) {
    tab.addEventListener("click", () => select(tab));
    tab.addEventListener("keydown", event => {
      const positions = {
        ArrowLeft: (index - 1 + tabs.length) % tabs.length,
        ArrowRight: (index + 1) % tabs.length,
        Home: 0,
        End: tabs.length - 1,
      };
      if (!Object.hasOwn(positions, event.key)) return;
      event.preventDefault();
      select(tabs[positions[event.key]], true);
    });
  }
  const deepLink = tabs.find(tab => "#" + tab.getAttribute("aria-controls") === window.location.hash);
  select(deepLink ?? tabs[0]);
}

function observeEntrances() {
  if (!("IntersectionObserver" in window)) return;
  const entries = new IntersectionObserver((items, observer) => {
    for (const { target, isIntersecting } of items) {
      if (!isIntersecting) continue;
      target.classList.remove("awaiting");
      target.classList.add("seen");
      observer.unobserve(target);
    }
  }, { threshold: 0.1 });
  for (const item of document.querySelectorAll("[data-reveal], .chart")) {
    if (!reducedMotion.matches && item.hasAttribute("data-reveal") && item.getBoundingClientRect().top > innerHeight) {
      item.classList.add("awaiting");
    }
    entries.observe(item);
  }
}

function setUpScroll() {
  const steps = [...document.querySelectorAll(".timeline-entry")];
  const stagePhoto = document.querySelector(".timeline-stage img");
  const stageCaption = document.querySelector(".timeline-stage figcaption");
  const wide = window.matchMedia("(min-width: 900px)");
  let requested = steps[0];
  let photoAnimation;
  let frame = 0;

  async function showStep(step) {
    if (step === requested) return;
    requested = step;
    const photo = step.querySelector("img");
    const next = new Image();
    next.src = photo.src;
    try {
      await next.decode();
    } catch {
      return;
    }

    if (step !== requested || stagePhoto.src === next.src) return;
    stagePhoto.src = next.src;
    stageCaption.textContent = step.querySelector("figcaption").textContent;
    photoAnimation?.cancel();
    if (!reducedMotion.matches) {
      photoAnimation = stagePhoto.animate([{opacity: .8}, {opacity: 1}], {duration: 150, easing: "ease-out"});
    }
  }

  function update() {
    frame = 0;
    if (wide.matches) {
      const readingLine = stagePhoto.getBoundingClientRect().top + 24;
      let candidate = steps[0];
      for (const step of steps) {
        if (step.getBoundingClientRect().top <= readingLine) candidate = step;
      }
      showStep(candidate);
    }
  }

  function schedule() {
    if (!frame) frame = requestAnimationFrame(update);
  }

  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  document.addEventListener("site-copy-change", () => {
    const showing = steps.find(step => step.querySelector("img").src === stagePhoto.src);
    if (showing) stageCaption.textContent = showing.querySelector("figcaption").textContent;
    schedule();
  });
  reducedMotion.addEventListener("change", schedule);
  schedule();
}

for (const lens of document.querySelectorAll("[data-lens]")) setUpLens(lens);
root.classList.add("js");
observeEntrances();
setUpScroll();
