PY ?= python3

.PHONY: check test validate scheme-ci clean

check: test validate   ## what CI runs

test:
	$(PY) -m pytest tests -q

validate:
	$(PY) tools/validate.py index

clean:
	rm -rf .pytest_cache $(shell find . -name __pycache__ -type d)
