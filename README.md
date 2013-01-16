## Installation
Editors' Notes requires Python 2.7 and PostgreSQL.

To set up a local development environment, install [Fabric](http://fabfile.org/) 
and make sure you have the following dependencies

* libxml2
* libxslt
* psycopg2
* [xapian](http://xapian.org/download) with python bindings

Run the command `fab setup` inside the project directory and edit the generated
"editorsnotes/settings\_local.py" file with your database information.  Finally, 
run the development server with `fab runserver`. 
