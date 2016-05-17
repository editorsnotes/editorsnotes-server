
SECRET_CHAR_CHOICES = 'abcdefghijklmnopqrstuvw1234567890+-_'
RANDOM_KEY = $(shell \
	     python -c 'import random; print("".join([random.choice("${SECRET_CHAR_CHOICES}") for i in range(50)]))')

setup: editorsnotes/settings_local.py lib
	@echo
	@echo Development environment succesfully created.
	@echo Create a Postgres database, enter its authentication information \
		into $<, and run make XXX to finish configuration.

refresh: lib static
	./manage.py migrate --noinput

clean:
	rm -rf bin lib include local man share static

.PHONY: setup refresh clean

lib: bin/pip requirements.txt bin/pip
	$< install -r $(word 2,$^)

bin/pip:
	virtualenv .

editorsnotes/settings_local.py:
	cp editorsnotes/example-settings_local.py $@
	sed -i -e "s/SECRET_KEY = ''/SECRET_KEY = '${RANDOM_KEY}'/" $@
