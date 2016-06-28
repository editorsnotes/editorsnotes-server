# Editors' Notes

[![Build status](https://travis-ci.org/editorsnotes/editorsnotes.svg)](https://travis-ci.org/editorsnotes/editorsnotes)

This Django application runs the Editors' Notes API and authentication server.


# Installation

## Dependencies

Editors' Notes currently uses **Python 3.5**.

This project depends on the Python package `lxml`, which has two dependencies:
`libxml2`, and `libxslt1`. They can be installed with your OS's package manager.

  * __Ubuntu/Debian__ (aptitude): `apt install libxml2-dev libxslt1-dev`
  * __Fedora/RHEL__ (dnf): `dnf install libxml2-devel libxslt-devel`
  * __OSX__ (homebrew): `brew install libxml2 libxslt && brew link libxml2 libxslt`

## Required services

Editors' Notes uses [PostgreSQL] (9.4+) and [Elasticsearch]. Consult the
documentation of those applications for installation instructions.

### Markup renderer

Text in the Editors' Notes API is a superset of the CommonMark markup standard. In
order to to render this text into HTML, this application requires a running
[Editors' Notes Markup Renderer Server]. By default, it will look for it on HTTP port
9393.


## Production deployment

See [editorsnotes/editorsnotes.org] for instructions on how to deploy Editors'
Notes on a server using nginx and uWSGI.


## Local development environment

  1. Run `make setup` at the project root directory. This will set up a virtual
     environment for python packages, install all dependencies, make a skeleton
     configuration file, and collect all necessary static files.

  2. Edit the skeleton settings file `editorsnotes/settings_local.py` with
     information about your system. The only setting you *must* fill out is
     your database configuration.

  3. Run `make all` to execute all database migrations

  4. Make sure that the markup renderer server is running

  5. Start the development server with `./venv/bin/python manage.py runserver`


[PostgreSQL]: http://www.postgresql.org/
[Elasticsearch]: https://www.elastic.co/products/elasticsearch
[editorsnotes/editorsnotes.org]: https://github.com/editorsnotes/editorsnotes.org
[Editors' Notes Markup Renderer Server]: https://github.com/editorsnotes/editorsnotes-markup-renderer
