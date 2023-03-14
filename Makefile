PACKAGE_NAME := copylot

.PHONY: setup-develop
setup-develop:
	pip install -r requirements/development.txt
	pip install -e .
	pre-commit install

.PHONY: uninstall
uninstall:
	pip uninstall -y $(PACKAGE_NAME)

.PHONY: check-format
check-format:
	black --check -S -t py39 .

.PHONY: lint
lint:
	flake8 $(PACKAGE_NAME)
	pylint $(PACKAGE_NAME)

# run the pre-commit hooks on all files (not just staged changes)
.PHONY: pre-commit
pre-commit:
	pre-commit run --all-files

.PHONY: test
test:
	python -m pytest . --disable-pytest-warnings
