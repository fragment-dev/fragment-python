.PHONY: lint

install:
	poetry install --with dev

lint: sort_order style typecheck

sort_order:
	poetry run isort fragment/

style:
	poetry run black fragment/

typecheck:
	poetry run mypy -p fragment

build: install
	poetry run fragment-python-client-codegen --queries-path=queries/ --target-package=sdk --target-package-path fragment/

docker-build:
	docker build -t fragment-python-sdk-dev .

docker-run: docker-build
	docker run -v ${CURDIR}:/app -w /app -it fragment-python-sdk-dev /bin/bash
