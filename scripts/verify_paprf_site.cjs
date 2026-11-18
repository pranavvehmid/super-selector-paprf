/* Execute against the served dashboard with playwright-core and installed Edge. */
const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium } = require("playwright-core");

const base = process.env.PAPRF_SITE_URL || "http://127.0.0.1:8765/";
const screenshots = process.env.PAPRF_SCREENSHOTS;
const routes = ["home", "dataset", "framework", "pressure", "players", "roles", "top-ten",
  "compare", "validation", "documentation", "about"];

function contrast(first, second) {
  const luminance = (rgb) => {
    const [r, g, b] = rgb.match(/\d+/g).slice(0, 3).map((value) => {
      const c = +value / 255;
      return c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4;
    });
    return .2126*r + .7152*g + .0722*b;
  };
  const [bright, dark] = [luminance(first), luminance(second)].sort((a, b) => b - a);
  return (bright + .05) / (dark + .05);
}

async function main() {
  const browser = await chromium.launch({channel: "msedge", headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 900}, colorScheme: "dark"});
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    if (process.env.PAPRF_KATEX_DIR) {
      await page.route("https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/**", async route => {
        const name = route.request().url().split("/dist/")[1];
        await route.fulfill({path:path.join(process.env.PAPRF_KATEX_DIR, name),headers:{"Access-Control-Allow-Origin":"*"}});
      });
    }
    await page.route("https://fonts.googleapis.com/**", r => r.abort());
    await page.goto(base, {waitUntil:"load"});
    assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
    for (const theme of ["dark", "light"]) {
      if (await page.locator("html").getAttribute("data-theme") !== theme) await page.locator("#theme-toggle").click();
      for (const width of [390, 768, 1280, 1440, 1920]) {
        await page.setViewportSize({width,height:900});
        for (const route of routes) {
          await page.locator(`a[data-route="${route}"]`).first().click();
          const current = page.locator("#atlas-nav [aria-current=page]");
          assert.equal(await current.getAttribute("data-route"), route);
          assert.match(page.url(), new RegExp(`page=${route}`));
          assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true,
                       `horizontal overflow on ${route} at ${width} in ${theme}`);
        }
      }
      await page.locator('a[data-route="top-ten"]').first().click();
      const styles = await page.evaluate(() => {
        const swatch = (selector, field) => getComputedStyle(document.querySelector(selector))[field];
        return [[swatch("body","color"),swatch("body","backgroundColor")],
                [swatch(".site-header nav a[aria-current=page]","color"),swatch(".site-header","backgroundColor")],
                [swatch("#unified-table th","color"),swatch("#unified-table th","backgroundColor")]];
      });
      assert.ok(styles.every(pair => contrast(...pair) >= 4.5), `${theme} text contrast`);
      if (screenshots) {
        await page.setViewportSize({width:1440,height:900});
        await page.screenshot({path:path.join(screenshots,`top-ten-${theme}.png`)});
      }
    }
    await page.locator("#unified-discipline").selectOption("bowler");
    assert.match(await page.locator("#unified-table tbody tr").first().innerText(), /Varun Chakravarthy/);
    assert.equal(await page.locator("#unified-table tbody tr").count(), 10);
    await page.locator('a[data-route="dataset"]').click();
    await page.locator("#dataset-fields").selectOption("missing");
    assert.match(await page.locator("#dataset-missing").innerText(), /dismissed_player_id/);
    await page.goBack();
    assert.equal(await page.locator("#atlas-nav [aria-current=page]").getAttribute("data-route"), "top-ten");
    await page.goto(new URL("?page=framework", base).href, {waitUntil:"load"});
    assert.equal(await page.locator("html").getAttribute("data-theme"), "light");
    assert.equal(await page.locator(".equation .katex").count(), 3);
    await page.locator('a[data-route="compare"]').focus();
    await page.keyboard.press("Enter");
    assert.match(await page.locator("#compare-matrix").innerText(), /Final contextual index/);
    await page.locator("#figure-select").selectOption("2");
    await page.waitForFunction(() => document.querySelector("#figure-image").naturalWidth > 0);
    assert.match(await page.locator("#figure-caption").innerText(), /Later-window role/);
    await page.goto(new URL("?page=documentation",base).href,{waitUntil:"load"});
    assert.match(await page.locator("#publication-run").innerText(), /Evidence run [a-f0-9]{12}/);
    for (const file of ["reports/paprf_research_source.zip","library.html"]) {
      assert.equal((await page.request.get(new URL(file,base).href)).status(),200);
    }
    if (await page.locator("#publication-pdf").isVisible()) {
      const response = await page.request.get(new URL("reports/paprf_research.pdf",base).href);
      assert.equal(response.status(),200);
      assert.match(response.headers()["content-type"],/application\/pdf/);
    }
    assert.deepEqual(errors, []);
    console.log("11 routes × 5 widths × 2 themes, contrast, keyboard, history, calculations and report downloads passed.");
  } finally { await browser.close(); }
}

main().catch(error => { console.error(error.stack || error); process.exitCode = 1; });
