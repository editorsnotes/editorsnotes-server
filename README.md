Editors' Notes API and authentication server.


# Required services

Editors' Notes uses [PostgreSQL] and [Elasticsearch]. Consult the documentation
of those applications for installation instructions.


# Dependencies

Editors' Notes currently uses **Python 2.7**.

This project depends on the Python package `lxml`, which has two dependencies:
`libxml2`, and `libxslt1`. They can be installed with your OS's package manager.

  * __Ubuntu__ (aptitude): `apt-get install libxml2-dev libxslt1-dev`
  * __Fedora__ (yum): `yum install libxml2-devel libxslt-devel`
  * __OSX__ (homebrew): `brew install libxml2 libxslt && brew link libxml2 libxslt`


# Deployment

See [editorsnotes/editorsnotes.org] for instructions on how to deploy Editors'
Notes on a server using nginx and uWSGI.


# Local development environment

Setting up a local environment requires the Python task runner [Fabric], which
can be installed with your package manager. Once it and the dependencies above
have been installed, perform the following steps:

  1. Run `fab setup` at the project root directory. This will set up a virtual
     environment for python packages, install all dependencies, make a skeleton
     configuration file, and collect all necessary static files.

  2. Edit the skeleton settings file `editorsnotes/settings_local.py` with
     information about your system. The only setting you *must* fill out is
     your database configuration.

  3. Run `fab sync_database` to execute all database migrations

  4. Start the development server with `fab runserver`

__FIXME: Add section about required editorsnotes-markup-renderer as well__


[PostgreSQL]: http://www.postgresql.org/
[Elasticsearch]: https://www.elastic.co/products/elasticsearch
[editorsnotes/editorsnotes.org]: https://github.com/editorsnotes/editorsnotes.org
[Fabric]: http://fabfile.org/
