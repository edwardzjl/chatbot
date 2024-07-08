
# Default target executed when no arguments are given to make.
all: help

lint:
	pipenv run ruff check
	pipenv run ruff format --check

format:
	pipenv run ruff check --fix
	pipenv run ruff format

test:
	pipenv run python -m unittest

######################
# HELP
######################

help:
	@echo '----'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo 'test                         - run unit tests'
