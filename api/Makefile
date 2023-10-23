
# Default target executed when no arguments are given to make.
all: help

lint:
	pipenv run black . --check

format:
	pipenv run black .

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
