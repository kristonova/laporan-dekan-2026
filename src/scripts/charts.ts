type InitializableRoot = Document | HTMLElement;

const initializedTooltips = new WeakSet<Element>();
const initializedCounts = new WeakSet<Element>();
const initializedReveals = new WeakSet<Element>();
const initializedSdgGrids = new WeakSet<Element>();
const initializedMaps = new WeakSet<Element>();
const initializedCrosshairs = new WeakSet<Element>();
const initializedTables = new WeakSet<Element>();
const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const idNumber = new Intl.NumberFormat("id-ID", { maximumFractionDigits: 1 });

function initTooltips(root: InitializableRoot): void {
  const targets = root.querySelectorAll<HTMLElement | SVGElement>("[data-tooltip]");
  if (!targets.length) return;

  let tooltip = document.querySelector<HTMLElement>("[data-chart-tooltip]");
  if (!tooltip) {
    tooltip = document.createElement("div");
    tooltip.id = "chart-tooltip";
    tooltip.dataset.chartTooltip = "";
    tooltip.setAttribute("role", "tooltip");
    tooltip.hidden = true;
    Object.assign(tooltip.style, {
      position: "fixed",
      zIndex: "1000",
      maxWidth: "min(22rem, calc(100vw - 2rem))",
      padding: "0.55rem 0.7rem",
      border: "1px solid rgba(255,255,255,.2)",
      borderRadius: ".4rem",
      background: "#0b1f2e",
      color: "#fff",
      boxShadow: "0 10px 30px rgba(11,31,46,.2)",
      font: "600 .78rem/1.45 system-ui, sans-serif",
      pointerEvents: "none",
    });
    document.body.append(tooltip);
  }

  const position = (eventTarget: Element, clientX?: number, clientY?: number) => {
    if (!tooltip) return;
    const rect = eventTarget.getBoundingClientRect();
    const x = clientX ?? rect.left + rect.width / 2;
    const y = clientY ?? rect.top;
    const gap = 14;
    const tooltipRect = tooltip.getBoundingClientRect();
    tooltip.style.left = `${Math.max(8, Math.min(window.innerWidth - tooltipRect.width - 8, x + gap))}px`;
    tooltip.style.top = `${Math.max(8, Math.min(window.innerHeight - tooltipRect.height - 8, y - tooltipRect.height - gap))}px`;
  };

  const show = (target: HTMLElement | SVGElement, clientX?: number, clientY?: number) => {
    if (!tooltip) return;
    tooltip.textContent = target.dataset.tooltip ?? "";
    tooltip.hidden = false;
    target.setAttribute("aria-describedby", tooltip.id);
    position(target, clientX, clientY);
  };

  const hide = (target: HTMLElement | SVGElement) => {
    if (!tooltip) return;
    tooltip.hidden = true;
    if (target.getAttribute("aria-describedby") === tooltip.id) target.removeAttribute("aria-describedby");
  };

  targets.forEach((target) => {
    if (initializedTooltips.has(target)) return;
    initializedTooltips.add(target);
    target.addEventListener("pointerenter", (event) => show(target, (event as PointerEvent).clientX, (event as PointerEvent).clientY));
    target.addEventListener("pointermove", (event) => position(target, (event as PointerEvent).clientX, (event as PointerEvent).clientY));
    target.addEventListener("pointerleave", () => hide(target));
    target.addEventListener("focus", () => show(target));
    target.addEventListener("blur", () => hide(target));
    target.addEventListener("keydown", (event) => {
      if ((event as KeyboardEvent).key === "Escape") hide(target);
    });
  });
}

function initCountUp(root: InitializableRoot): void {
  root.querySelectorAll<HTMLElement>("[data-count-up]").forEach((element) => {
    if (initializedCounts.has(element)) return;
    initializedCounts.add(element);
    const target = Number(element.dataset.countUp || element.dataset.target || element.textContent?.replace(/[^\d,.-]/g, "").replace(",", "."));
    if (!Number.isFinite(target) || prefersReducedMotion()) return;
    const prefix = element.dataset.countPrefix ?? "";
    const suffix = element.dataset.countSuffix ?? "";
    const duration = Math.min(600, Math.max(300, Number(element.dataset.countDuration) || 600));
    const decimals = Math.max(0, Number(element.dataset.countDecimals) || 0);
    const formatter = new Intl.NumberFormat("id-ID", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

    const run = () => {
      const started = performance.now();
      const frame = (now: number) => {
        const progress = Math.min(1, (now - started) / duration);
        const eased = 1 - (1 - progress) ** 3;
        element.textContent = `${prefix}${formatter.format(target * eased)}${suffix}`;
        if (progress < 1) requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    };

    if (!("IntersectionObserver" in window)) {
      run();
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      observer.disconnect();
      run();
    }, { threshold: 0.45 });
    observer.observe(element);
  });
}

function initLineCrosshairs(root: InitializableRoot): void {
  root.querySelectorAll<SVGSVGElement>("svg[data-line-chart]").forEach((chart) => {
    const crosshair = chart.querySelector<SVGLineElement>("[data-chart-crosshair]");
    if (!crosshair || initializedCrosshairs.has(crosshair)) return;
    initializedCrosshairs.add(crosshair);
    chart.querySelectorAll<SVGCircleElement>("[data-crosshair-x]").forEach((marker) => {
      const show = () => {
        const x = marker.dataset.crosshairX;
        if (!x) return;
        crosshair.setAttribute("x1", x);
        crosshair.setAttribute("x2", x);
        crosshair.style.display = "";
      };
      const hide = () => { crosshair.style.display = "none"; };
      marker.addEventListener("pointerenter", show);
      marker.addEventListener("pointerleave", hide);
      marker.addEventListener("focus", show);
      marker.addEventListener("blur", hide);
    });
  });
}

function initReveal(root: InitializableRoot): void {
  if (prefersReducedMotion()) return;
  root.querySelectorAll<HTMLElement>("[data-reveal]").forEach((element) => {
    if (initializedReveals.has(element)) return;
    initializedReveals.add(element);
    if (!("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      observer.disconnect();
      const delay = Math.max(0, Math.min(240, Number(element.dataset.revealDelay) || 0));
      element.animate(
        [
          { opacity: 0, transform: "translateY(24px) scale(0.992)" },
          { opacity: 1, transform: "translateY(0) scale(1)" },
        ],
        { duration: 560, delay, easing: "cubic-bezier(0.2, 0.8, 0.2, 1)", fill: "both" },
      );
    }, { threshold: 0.12, rootMargin: "0px 0px -8%" });
    observer.observe(element);
  });
}

function initSdgGrids(root: InitializableRoot): void {
  root.querySelectorAll<HTMLElement>("[data-sdg-grid]").forEach((grid) => {
    if (initializedSdgGrids.has(grid)) return;
    initializedSdgGrids.add(grid);
    const controls = grid.querySelector<HTMLElement>("[data-sdg-controls]");
    const buttons = [...grid.querySelectorAll<HTMLButtonElement>("[data-sdg-mode]")];
    if (!controls || buttons.length < 2) return;
    controls.hidden = false;
    grid.classList.add("is-enhanced");

    const selectMode = (mode: string) => {
      buttons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.sdgMode === mode)));
      grid.querySelectorAll<HTMLElement>("[data-sdg-card]").forEach((card) => {
        const values = [...card.querySelectorAll<HTMLElement>("[data-mode-value]")];
        values.forEach((value) => { value.hidden = value.dataset.modeValue !== mode; });
        const active = values.find((value) => value.dataset.modeValue === mode);
        const fill = Number(active?.dataset.fill ?? 0);
        card.style.setProperty("--sdg-fill", `${fill}%`);
        const numeric = Number(active?.dataset.rawValue ?? 0);
        card.classList.toggle("is-zero", numeric === 0);
      });
    };

    buttons.forEach((button) => button.addEventListener("click", () => selectMode(button.dataset.sdgMode ?? "")));
    selectMode(grid.dataset.defaultMode ?? buttons[0].dataset.sdgMode ?? "");
  });
}

function initPointMaps(root: InitializableRoot): void {
  root.querySelectorAll<HTMLElement>("[data-point-map]").forEach((map) => {
    if (initializedMaps.has(map)) return;
    initializedMaps.add(map);
    const controls = map.querySelector<HTMLElement>("[data-map-controls]");
    const buttons = [...map.querySelectorAll<HTMLButtonElement>("[data-map-year]")];
    const points = [...map.querySelectorAll<SVGGElement>("[data-map-point]")];
    const output = map.querySelector<HTMLOutputElement>("[data-map-output]");
    const outputYear = map.querySelector<HTMLElement>("[data-map-output-year]");
    if (!controls || buttons.length < 2) return;
    controls.hidden = false;
    const accumulate = map.dataset.accumulate !== "false";
    const unit = map.dataset.pointLabel ?? "kegiatan";

    const selectYear = (year: string) => {
      buttons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.mapYear === year)));
      let total = 0;
      points.forEach((point) => {
        const pointYear = point.dataset.year ?? "";
        const visible = !pointYear || (accumulate ? Number(pointYear) <= Number(year) : pointYear === year);
        point.classList.toggle("is-map-hidden", !visible);
        point.setAttribute("aria-hidden", String(!visible));
        point.setAttribute("tabindex", visible ? "0" : "-1");
        if (visible) total += Number(point.dataset.value ?? 0);
      });
      if (output) output.textContent = `${idNumber.format(total)} ${unit}`;
      if (outputYear) outputYear.textContent = `${accumulate ? " · hingga" : " · tahun"} ${year}`;
    };

    buttons.forEach((button) => button.addEventListener("click", () => selectYear(button.dataset.mapYear ?? "")));
    selectYear(map.dataset.defaultYear ?? buttons.at(-1)?.dataset.mapYear ?? "");
  });
}

function initTableDialogs(root: InitializableRoot): void {
  root.querySelectorAll<HTMLDetailsElement>(".chart-frame__table-wrap").forEach((details) => {
    if (initializedTables.has(details)) return;
    initializedTables.add(details);
    details.addEventListener("keydown", (event) => {
      if (event.key !== "Escape" || !details.open) return;
      details.open = false;
      details.querySelector<HTMLElement>("summary")?.focus();
    });
  });
}

export function initChartEnhancements(root: InitializableRoot = document): void {
  initTooltips(root);
  initCountUp(root);
  initLineCrosshairs(root);
  initReveal(root);
  initSdgGrids(root);
  initPointMaps(root);
  initTableDialogs(root);
}

if (typeof document !== "undefined") {
  const start = () => initChartEnhancements(document);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
  document.addEventListener("astro:page-load", start);
}
