# PAPRF native LaTeX report

The source archive contains the main document, generated tables, and its referenced figure. Extract to a directory and run tectonic paprf_research.tex from that directory. A full TeX installation can instead run latexmk -pdf paprf_research.tex. The font pairing uses the Times-compatible mathptmx package.

In this repository run python scripts/verify_paprf_rebuild.py against the original six CSV files, then run python scripts/build_paprf_latex.py --engine followed by the full path to Tectonic. The generator derives tables from the versioned ranking outputs and writes the evidence run ID. Run it without the engine option to generate sources only.
