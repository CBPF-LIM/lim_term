.PHONY: lint run lang-check lang-sync lang-format

default: run

lint:
	poetry run black .

run:
	poetry run limterm

lang-check:
	poetry run python dev-tools/validate_languages.py limterm/languages

lang-sync:
	poetry run python dev-tools/sync_languages.py limterm/languages

lang-format:
	poetry run python dev-tools/format_yaml_files.py

setup:
	poetry install

install:
	pipx install .

shell:
	poetry run python

pipx:
	sudo apt install pipx
	python3 -m pipx ensurepath
