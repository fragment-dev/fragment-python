.PHONY: lint test

install:
	poetry install --with dev

lint: sort_order style typecheck

sort_order:
	poetry run isort fragment/ tests/

style:
	poetry run black fragment/ tests/

typecheck:
	poetry run mypy -p fragment

# Integration tests. Requires CLIENT_ID, CLIENT_SECRET, SCOPE, AUTH_URL and
# API_URL in the environment; the tests fail if any are missing.
test:
	poetry run pytest

build: install
	poetry run fragment-python-client-codegen --input-dir=queries/ --target-package-name=sdk --output-dir fragment/
	poetry run fragment-python-client-codegen --input-dir=queries/ --target-package-name=sync_sdk --output-dir fragment/ --sync

docker-build:
	docker build -t fragment-python-sdk-dev .

docker-run: docker-build
	docker run -v ${CURDIR}:/app -w /app -it fragment-python-sdk-dev /bin/bash
