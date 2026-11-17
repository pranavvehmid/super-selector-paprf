.PHONY: setup test check log
setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
test:
	pytest -q
check:
	python scripts/check_data_pack.py
# usage: make log STEP=4 MSG="Rebuilt pre-delivery state" FILES="src/rrselect/state.py"
log:
	python scripts/log_progress.py --step "$(STEP)" --summary "$(MSG)" --files "$(FILES)"
