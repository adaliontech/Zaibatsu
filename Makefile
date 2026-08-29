.PHONY: validate test droid-preflight

validate: test
	python3 scripts/validate_repository.py

test:
	python3 -m unittest discover -s tests -v

droid-preflight:
	python3 scripts/droid_preflight.py
