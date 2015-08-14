help:
	@echo "clean - remove Python file artifacts"
	@echo "clean-all - remove *all* build artifacts"
	@echo "clean-env - remove virtual environment"
	@echo "deps - install the dependencies"
	@echo "env - set up the virtual environment"
	@echo "test - run tests"
	@echo "test-deps - install the dependencies needed for running tests"

###########
# VARIABLES
###########
ENV := env/
BIN := $(ENV)bin/
NOSETESTS := $(BIN)nosetests
PIP := $(BIN)pip
PYTHON := $(BIN)python

#######
# SETUP
#######
$(BIN)python:
	virtualenv env

$(BIN)pip:
	virtualenv env

.PHONY: env
env: $(BIN)python

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
$(NOSETESTS): $(BIN)python
	$(MAKE) test-deps

#####################
# DEVELOPMENT HELPERS
#####################

.PHONY: test
test: $(NOSETESTS)
	$(NOSETESTS)

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
	rm -rf env

.PHONY: clean-all
clean-all: clean clean-env
	rm -rf jujulib.egg-info/
