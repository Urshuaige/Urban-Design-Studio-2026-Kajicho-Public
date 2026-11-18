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
  const studioNav = [...document.querySelectorAll('.masthead nav a[href^="#"]')];
  const navSections = studioNav.map(link => document.querySelector(link.hash));
  const wide = window.matchMedia("(min-width: 900px)");
  let requested = steps[0];
  let changing = 0;
  let frame = 0;

  function showStep(step) {
    if (step === requested) return;
    requested = step;
    const photo = step.querySelector("img");
    const caption = step.querySelector("figcaption");
    const next = new Image();
    const sequence = ++changing;
    next.onload = () => {
      if (sequence !== changing) return;
      const swap = () => {
        if (sequence !== changing) return;
        stagePhoto.src = next.src;
        stageCaption.textContent = caption.textContent;
        stagePhoto.classList.remove("changing");
      };
      if (reducedMotion.matches) {
        swap();
      } else {
        stagePhoto.classList.add("changing");
        window.setTimeout(swap, 150);
      }
    };
    next.onerror = () => {
      if (sequence === changing) stagePhoto.classList.remove("changing");
    };
    next.src = photo.src;
  }

  function update() {
    frame = 0;
    const distance = root.scrollHeight - innerHeight;
    root.style.setProperty("--reading-progress", distance > 0 ? Math.min(scrollY / distance, 1) : 0);
    root.style.setProperty("--hero-shift", reducedMotion.matches ? "0px" : Math.min(scrollY * .08, 28) + "px");
    let activeNav = -1;
    for (const [index, section] of navSections.entries()) {
      const { top, bottom } = section.getBoundingClientRect();
      if (top < innerHeight * .42 && bottom > innerHeight * .25) activeNav = index;
    }
    for (const [index, link] of studioNav.entries()) {
      if (index === activeNav) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }

    if (wide.matches) {
      let candidate = steps[0];
      for (const step of steps) {
        if (step.getBoundingClientRect().top <= innerHeight * .53) candidate = step;
      }
      showStep(candidate);
    }
  }

  function schedule() {
    if (!frame) frame = requestAnimationFrame(update);
  }

  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  reducedMotion.addEventListener("change", schedule);
  schedule();
}

for (const lens of document.querySelectorAll("[data-lens]")) setUpLens(lens);
root.classList.add("js");
observeEntrances();
setUpScroll();
