.PHONY: lint test snapshots check-snapshots

# Each tests/snapshots/*/ holds a queries.graphql and the client generated from
# it, checked in. The pair is a regression guard: a change to codegen that alters
# generated output shows up as a reviewable diff instead of silently.
SNAPSHOT_DIRS := $(sort $(dir $(wildcard tests/snapshots/*/queries.graphql)))
SNAPSHOT_PACKAGE := sdk

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

# Overwrite the checked-in snapshots with freshly generated clients. Run this
# deliberately after an intended codegen change, then review the diff before
# committing it.
snapshots:
	@for dir in $(SNAPSHOT_DIRS); do \
		echo "Regenerating $$dir$(SNAPSHOT_PACKAGE)"; \
		rm -rf "$$dir$(SNAPSHOT_PACKAGE)"; \
		poetry run fragment-python-client-codegen \
			--input-dir="$$dir" \
			--target-package-name=$(SNAPSHOT_PACKAGE) \
			--output-dir="$$dir" || exit 1; \
	done
	poetry run isort tests/snapshots/
	poetry run black tests/snapshots/

# Regenerate in place and fail if anything changed. Used in CI so generated
# output cannot drift from the committed snapshots.
check-snapshots: snapshots
	@untracked="$$(git ls-files --others --exclude-standard -- tests/snapshots)"; \
	if ! git diff --quiet -- tests/snapshots || [ -n "$$untracked" ]; then \
		echo ""; \
		echo "Generated client differs from the committed snapshots."; \
		echo "If the change is intended, run 'make snapshots' and commit the result."; \
		echo ""; \
		git --no-pager diff --stat -- tests/snapshots; \
		[ -n "$$untracked" ] && printf 'untracked:\n%s\n' "$$untracked"; \
		exit 1; \
	fi
	@echo "Snapshots up to date."

build: install
	poetry run fragment-python-client-codegen --input-dir=queries/ --target-package-name=sdk --output-dir fragment/
	poetry run fragment-python-client-codegen --input-dir=queries/ --target-package-name=sync_sdk --output-dir fragment/ --sync

docker-build:
	docker build -t fragment-python-sdk-dev .

docker-run: docker-build
	docker run -v ${CURDIR}:/app -w /app -it fragment-python-sdk-dev /bin/bash
