
# Default target executed when no arguments are given to make.
all: help

lint:
	npx eslint . --ext .js,.jsx,.ts,.tsx

format:
	npx eslint . --ext .js,.jsx,.ts,.tsx --fix

test:
	yarn test

######################
# HELP
######################

help:
	@echo '----'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo 'test                         - run unit tests'
