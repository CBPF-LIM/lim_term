.PHONY: lint run

default: run

lint:
	poetry run black .

run:
	poetry run limterm

requirements:
	poetry install

install:
	pipx install .

pipx:
	sudo apt install pipx
	python3 -m pipx ensurepath