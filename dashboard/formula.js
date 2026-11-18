"use strict";
for (const node of document.querySelectorAll("[data-tex]")) {
  if (globalThis.katex) globalThis.katex.render(node.dataset.tex, node,
    {displayMode: node.dataset.display !== "inline", throwOnError: false});
}
