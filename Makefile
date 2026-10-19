install:
	uv sync

run:
	uv run database

build:
	uv build

package-install:
	uv tool install --force dist/*.whl

lint:
	uv run ruff check .

.PHONY: install run build package-install lint
