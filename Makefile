.PHONY: lint

lint: sort_order style

sort_order:
	poetry run isort fragment/

style:
	poetry run black fragment/
