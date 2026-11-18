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
    await page.route(/^https?:\/\//, r => new URL(r.request().url()).origin === new URL(base).origin ? r.continue() : r.abort());
    await page.goto(base, {waitUntil:"load"});
    assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
    assert.equal(await page.locator("main > section:visible").first().locator("h1").innerText(), "Ultimate Top 10");
    const expectedHome = await page.evaluate(() => ["batter", "bowler"].map(discipline =>
      globalThis.paprfEvidence.disciplines.lists[discipline].top10.map(r => [String(r.rank), r.name, r.score.toFixed(3)])));
    assert.deepEqual(expectedHome.map(rows => rows.length), [10, 10]);
    const actualHome = await page.locator("#home-preview table").evaluateAll(tables => tables.map(table =>
      Array.from(table.tBodies[0].rows, row => Array.from(row.cells, cell => cell.textContent))));
    assert.deepEqual(actualHome, expectedHome);
    assert.match(await page.locator("#home-rankings .report-link").getAttribute("href"), /round1_submission\.pdf$/);
    await page.locator("#home-preview a").last().click();
    assert.match(await page.locator("#unified-player h3").innerText(), /Bhuvneshwar Kumar/);
    assert.equal(await page.locator("#unified-discipline").inputValue(), "bowler");
    await page.reload();
    assert.match(await page.locator("#unified-player h3").innerText(), /Bhuvneshwar Kumar/);
    await page.goBack();
    assert.equal(await page.locator("#home-rankings").isVisible(), true);
    for (const theme of ["dark", "light"]) {
      if (await page.locator("html").getAttribute("data-theme") !== theme) await page.locator("#theme-toggle").click();
      for (const width of [390, 768, 1280, 1440, 1920]) {
        await page.setViewportSize({width,height:900});
        for (const route of routes) {
          const toggle = page.locator("#sections-toggle");
          if (await toggle.isVisible()) await toggle.click();
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
                [swatch("#atlas-nav a[aria-current=page]","color"),swatch("#atlas-nav a[aria-current=page]","backgroundColor")],
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
    assert.equal(await page.locator("#pipeline .katex, #method .katex").count(), 6);
    await page.setViewportSize({width: 390, height: 844});
    await page.locator('#pipeline a[href="#method"]').click();
    assert.equal(new URL(page.url()).hash, "#method");
    assert.ok(await page.locator("#eq-pressure .katex").isVisible());
    const fits = await page.locator("#pipeline .equation > span, #method .equation > span")
      .evaluateAll(nodes => nodes.every(node => node.scrollWidth <= node.clientWidth + 2));
    assert.ok(fits, "all six main equations fit at 390px");
    await page.locator("#sections-toggle").click();
    await page.locator("#atlas-nav a").first().focus();
    await page.keyboard.press("Escape");
    assert.equal(await page.locator("#sections-toggle").getAttribute("aria-expanded"), "false");
    await page.setViewportSize({width: 1440, height: 900});
    await page.locator('a[data-route="compare"]').focus();
    await page.keyboard.press("Enter");
    assert.match(await page.locator("#compare-matrix").innerText(), /Final contextual index/);
    await page.locator("#figure-select").selectOption("2");
    await page.waitForFunction(() => document.querySelector("#figure-image").naturalWidth > 0);
    assert.match(await page.locator("#figure-caption").innerText(), /Later-window role/);
    await page.goto(new URL("?page=documentation",base).href,{waitUntil:"load"});
    assert.match(await page.locator("#publication-run").innerText(), /Evidence run [a-f0-9]{12}/);
    for (const file of ["reports/round1_submission.pdf","reports/paprf_research_source.zip","library.html"]) {
      assert.equal((await page.request.get(new URL(file,base).href)).status(),200);
    }
    await page.goto(new URL("?page=pressure",base).href,{waitUntil:"load"});
    for (const role of ["batter", "bowler"]) {
      await page.locator("#role").selectOption(role);
      const frozen = await page.evaluate(role => globalThis.paprfEvidence.rankings[role].map(r => r.player_name),role);
      assert.deepEqual(await page.locator("#rank-rows button").allTextContents(), frozen);
      await page.locator("#rank-rows button").last().click();
      assert.equal(await page.locator("#player h3").innerText(), frozen[9]);
      assert.equal(await page.locator("#player .metric-bar").count(), 6);
    }
    await page.goto(new URL("?page=validation", base).href,{waitUntil:"load"});
    assert.match(await page.locator("#validation-summary").innerText(), /5 of 6/);
    if (await page.locator("#publication-pdf").isVisible()) {
      const response = await page.request.get(new URL("reports/paprf_research.pdf",base).href);
      assert.equal(response.status(),200);
      assert.match(response.headers()["content-type"],/application\/pdf/);
    }
    await page.locator('a[data-route="about"]').click();
    const author = await page.evaluate(() => globalThis.paprfAuthor);
    assert.equal(await page.locator("#about h1").innerText(), `About ${author.name}`);
    assert.equal(await page.locator('#about [data-author="bio"]').innerText(), author.bio);
    const contactLinks = await page.locator("#author-links a").evaluateAll(links => links.map(link => link.getAttribute("href")));
    assert.deepEqual(contactLinks, [`mailto:${author.email}`, `tel:${author.phone.replace(/\s/g, "")}`, author.linkedin, author.repository]);
    await page.goto(new URL("library.html#formula-reference", base).href, {waitUntil:"load"});
    assert.equal(await page.locator("#formula-reference .equation .katex").count(), 12);
    assert.equal(await page.locator("#formula-reference .katex-error").count(), 0);
    assert.equal(await page.evaluate(async () => {
      await document.fonts.ready;
      return [...document.fonts].some(font => font.family === "KaTeX_Main" && font.status === "loaded");
    }), true);
    assert.deepEqual(errors, []);
    console.log("11 routes × 5 widths × 2 themes, contrast, keyboard, history, calculations and report downloads passed.");
  } finally { await browser.close(); }
}

main().catch(error => { console.error(error.stack || error); process.exitCode = 1; });
