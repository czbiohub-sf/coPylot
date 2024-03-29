PACKAGE_NAME := copylot

.PHONY: setup-develop
setup-develop:
	pip install -r requirements/development.txt
	pip install -e .

.PHONY: uninstall
uninstall:
	pip uninstall -y $(PACKAGE_NAME)

.PHONY: check-format
check-format:
	black --check -S -t py39 .

.PHONY: format
format:
	black -S -t py39 .

.PHONY: lint
lint:
	flake8 $(PACKAGE_NAME)
	pylint $(PACKAGE_NAME) --extension-pkg-whitelist=PyQt5

# run the pre-commit hooks on all files (not just staged changes)
# (requires pre-commit to be installed)
.PHONY: pre-commit
pre-commit:
	pre-commit run

.PHONY: test
test:
	python -m pytest . --disable-pytest-warnings
