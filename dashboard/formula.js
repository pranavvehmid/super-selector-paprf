"use strict";
for (const node of document.querySelectorAll("[data-tex]")) {
  const displayMode = node.dataset.display !== "inline";
  if (globalThis.katex) {
    try {
      globalThis.katex.render(node.dataset.tex, node, {displayMode, throwOnError: true});
    } catch (error) {
      console.warn("PAPRF formula retained as text", error.message);
    }
  }
  if (displayMode) {
    node.tabIndex = 0;
    node.setAttribute("role", "group");
    node.setAttribute("aria-label", "Equation");
  }
}
