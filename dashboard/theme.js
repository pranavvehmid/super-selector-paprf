"use strict";
(() => {
  const key = "paprf-theme";
  const preference = matchMedia("(prefers-color-scheme: dark)");
  const saved = () => {
    try { return localStorage.getItem(key); } catch { return null; }
  };
  const apply = (theme) => {
    document.documentElement.dataset.theme = theme;
    const button = document.getElementById("theme-toggle");
    if (button) {
      button.textContent = theme === "dark" ? "Light mode" : "Dark mode";
      button.setAttribute("aria-pressed", String(theme === "dark"));
    }
  };
  apply(saved() || (preference.matches ? "dark" : "light"));
  preference.addEventListener("change", () => {
    if (!saved()) apply(preference.matches ? "dark" : "light");
  });
  document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("theme-toggle");
    apply(document.documentElement.dataset.theme);
    button?.addEventListener("click", () => {
      const mode = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      try { localStorage.setItem(key, mode); } catch { /* toggle remains usable */ }
      apply(mode);
    });
  });
})();
