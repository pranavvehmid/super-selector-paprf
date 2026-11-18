# PAPRF dashboard

The dashboard is a static HTML, CSS and JavaScript app. Python exports the audited aggregate tables at the repository root. The browser filters and compares those tables locally. This workload uses no server or WebAssembly runtime.

```powershell
python scripts/build_dashboard_data.py
python -m http.server 8765 --bind 127.0.0.1 --directory dashboard
```

When updating the publication, regenerate the index and library before deployment:

```powershell
python scripts/build_paprf_unified_ranking.py
python scripts/build_paprf_discipline_rankings.py
python scripts/verify_paprf_rebuild.py
python scripts/build_paprf_latex.py --engine <path-to-tectonic>
python scripts/build_dashboard_data.py
python scripts/build_paprf_research_library.py
```

The research-library builder uses the pinned Markdown package in `requirements.txt`. The site serves KaTeX, Inter and Source Serif 4 from its own domain. Readable equation text remains in place if the renderer is unavailable. The figure atlas serves selected generated plots with interpretations and chapter references.

Open http://127.0.0.1:8765. The page also works by opening index.html directly because the evidence export is bundled as a local script.

Use `?page=top-ten` for the separate batting and bowling indices, or use the top navigation to switch to the archived pressure evidence, role rankings, comparison tools or research documentation. The Documentation view links to the compiled report and editable source archive. Public author fields live in `author.js`. The [publication QA record](../docs/research/paprf_publication_qa.md) explains the rebuild and checks.

The export verifies the frozen top tens against the Phase 2 replay and reconciles the pressure distribution with the audit. It includes the ranking and sensitivity evidence, exposure counts, peer statistics, and aggregate player counts. Raw deliveries, the supplied archive and local credentials stay outside the hosted directory. Update the project milestone list in index.html when a phase changes and regenerate evidence.js after changing the inputs. Commit both source changes and the regenerated export.

## GitHub and Vercel

Sign in via the browser with `gh auth login --hostname github.com --git-protocol https --web`. A private repo named super-selector-paprf is the initial target. The GitHub CLI can create it and push the reviewed project commit once this machine is authenticated.

In Vercel, import the repository from GitHub and grant the Vercel integration access to that repo. Set Root Directory to dashboard and Framework Preset to Other. Use the default static output and leave the build command empty. Future pushes to the connected production branch redeploy the committed bundle. A private GitHub repository does not make the Vercel site private. Choose Vercel deployment protection if you want to restrict dashboard access.

Official setup references are the [GitHub CLI sign-in guide](https://cli.github.com/manual/gh_auth_login) and [Vercel build settings](https://vercel.com/docs/builds/configure-a-build).
