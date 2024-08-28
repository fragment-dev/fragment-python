.PHONY: lint

install:
	poetry install --with dev

lint: sort_order style

sort_order:
	poetry run isort fragment/

style:
	poetry run black fragment/

build: install
	poetry run fragment-python-client-codegen --queries-path=queries/ --target-package=fragment_graphql_client
