help:
	@echo "check - clean the environment, install, lint, and run tests"
	@echo "clean - remove Python file artifacts"
	@echo "clean-all - remove *all* build artifacts"
	@echo "clean-env - remove virtual environment"
	@echo "deps - install the dependencies"
	@echo "env - set up the virtual environment"
	@echo "lint - check Python lint"
	@echo "test - run tests"
	@echo "test-deps - install the dependencies needed for running tests"

###########
# VARIABLES
###########
ENV := .venv
BIN := $(ENV)/bin
FLAKE8 := $(BIN)/flake8
PIP := $(BIN)/pip
PYTEST := $(BIN)/py.test
PYTHON := $(BIN)/python
CANARY_REQ := .canary_requirements
CANARY_TEST_REQ := .canary_test_requirements

#######
# SETUP
#######
$(PYTHON):
	virtualenv $(ENV)

$(PIP):
	virtualenv $(ENV)

$(ENV): $(PYTHON)

##############
# DEPENDENCIES
##############
.PHONY: test-deps
test-deps: $(CANARY_TEST_REQ) deps

$(CANARY_TEST_REQ): $(PIP) test-requirements.txt
	$(PIP) install -r test-requirements.txt
	touch $(CANARY_TEST_REQ)

.PHONY: deps
deps: $(CANARY_REQ)

$(CANARY_REQ): $(PIP) requirements.txt
	$(PIP) install -r requirements.txt
	touch $(CANARY_REQ)

#####################
# DEVELOPMENT HELPERS
#####################

.PHONY: test
test: test-deps
	$(PYTEST) tests

.PHONY: lint
lint: test-deps
	$(FLAKE8) juju tests

.PHONY: check
check: clean-all lint test

###############
# CLEAN TARGETS
###############
.PHONY: clean
clean:
	find . -name $(ENV) -prune  -o -name '*.pyc' -exec rm -f {} +
	find . -name $(ENV) -prune -o -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

.PHONY: clean-env
clean-env:
	rm -rf $(ENV)
	rm -f $(CANARY_REQ)
	rm -f $(CANARY_TEST_REQ)

.PHONY: clean-all
clean-all: clean clean-env
	rm -rf jujulib.egg-info/
