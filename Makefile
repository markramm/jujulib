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
ENV := env/
BIN := $(ENV)bin/
FLAKE8 := $(BIN)flake8
NOSETESTS := $(BIN)nosetests
PIP := $(BIN)pip
PYTHON := $(BIN)python

#######
# SETUP
#######
$(PYTHON):
	virtualenv $(ENV)

$(PIP):
	virtualenv $(ENV)

.PHONY: env
env: $(PYTHON)

##############
# DEPENDENCIES
##############
.PHONY: test-deps
test-deps: $(PIP)
	$(PIP) install -r test-requirements.txt

.PHONY: deps
deps: $(PIP)
	$(PIP) install -r requirements.txt

# Nose is our test requirements canary
$(NOSETESTS): $(PYTHON) deps
	$(MAKE) test-deps

$(FLAKE8): $(NOSETESTS)

#####################
# DEVELOPMENT HELPERS
#####################

.PHONY: test
test: $(NOSETESTS)
	$(NOSETESTS)

.PHONY: lint
lint: $(FLAKE8)
	$(FLAKE8) juju tests

.PHONY: check
check: clean-all lint test

###############
# CLEAN TARGETS
###############
.PHONY: clean
clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

.PHONY: clean-env
clean-env:
	rm -rf $(ENV)

.PHONY: clean-all
clean-all: clean clean-env
	rm -rf jujulib.egg-info/
