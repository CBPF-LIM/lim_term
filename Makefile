.PHONY: lint run

lint:
	poetry run black .

run:
	poetry run python -m limterm.main
