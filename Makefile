VIRTUALENV_DIR ?= 'venv'

PIP = $(VIRTUALENV_DIR)/bin/pip
PYTHON = $(VIRTUALENV_DIR)/bin/python
PYTHONLIBS = $(VIRTUALENV_DIR)/lib

SECRET_KEY_CHARS = 'abcdefghijklmnopqrstuvw1234567890+-_'


#######

all: $(PYTHON) $(PYTHONLIBS) static
	$< manage.py migrate --noinput

setup: $(PYTHONLIBS) editorsnotes/settings_local.py
	@echo
	@echo
	@echo Development environment succesfully created.
	@echo
	@echo Create a Postgres database, enter its authentication information \
		into $(word 2, $^), and run make all to finish configuration.
	@echo
	@echo


clean:
	rm -rf venv tmp

.PHONY: setup refresh clean


#######

$(PYTHON):
	virtualenv venv -p python3

$(PYTHONLIBS): $(PYTHON) requirements.txt
	$(PIP) install -r $(word 2, $^)

static: $(PYTHON)
	$< manage.py collectstatic

tmp:
	mkdir -p tmp

tmp/secret_key: | tmp
	python -c 'import random; print("".join([random.choice("${SECRET_KEY_CHARS}") for i in range(50)]))' > $@

tmp/cache_filename: | tmp
	python -c 'import tempfile; print(tempfile.mktemp(prefix="workingnotes-"))' > $@

editorsnotes/settings_local.py: editorsnotes/example-settings_local.py tmp/secret_key tmp/cache_filename
	sed \
		-e "s|SECRET_KEY = ''|SECRET_KEY = '$(shell cat $(word 2, $^))'|" \
		-e "s|CACHE_FILENAME = ''|CACHE_FILENAME = '$(shell cat $(word 3, $^))'|" \
		$< > $@
	rm $(word 2, $^) $(word 3, $^)
	rmdir --ignore-fail-on-non-empty tmp
