#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fabfile for Django
------------------
see http://morethanseven.net/2009/07/27/fabric-django-git-apache-mod_wsgi-virtualenv-and-p/

modified for fabric 0.9/1.0 by Hraban (fiëé visuëlle)
several additions, corrections and customizations, too

This fabric file makes setting up and deploying a Django application much
easier, but it does make a few assumptions. Namely that you're using Git,
Apache and `mod_wsgi` and you're using Debian or Ubuntu. Also you should have 
Django installed on your local machine and SSH installed on both the local
machine and any servers you want to deploy to.

_note that I've used the name project_name throughout this example. Replace
this with whatever your project is called._

First step is to create your project locally:

    mkdir project_name
    cd project_name
    django-admin.py startproject project_name

Now add a requirements file so pip knows to install Django. You'll probably
add other required modules in here later. Create a file called `requirements.txt`
and save it at the top level with the following contents:

    Django

(Add other requirements at will, e.g. django-tinymce)
    
Then save this `fabfile.py` file (this gist!) in the top level directory
which should give you:
    
    project_name/
        fabfile.py
        requirements.txt
        project_name/
            __init__.py
            manage.py
            settings.py
            urls.py

You'll need a WSGI file called `django.wsgi`. It will probably look 
like the following, depending on your specific paths and the location
of your settings module

    import os
    import sys

    # put the Django project on sys.path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__))))

    os.environ["DJANGO_SETTINGS_MODULE"] = "project_name.settings"

    from django.core.handlers.wsgi import WSGIHandler
    application = WSGIHandler()

Last but not least you'll want a virtualhost file for apache which looks 
something like the following. Save this as `vhost.conf` in the inner directory.
You'll want to change `/path/to/project_name/` to the location on the remote
server you intent to deploy to.

	<VirtualHost *:80>
	    ServerName      www.project_name.com
	    ServerAlias     project_name.example.com # temporary location
	
	    # disable listing and "guessing" of static files
	    <Directory /var/www/>
	            Options -Indexes FollowSymLinks -MultiViews
	            AllowOverride None
	            Order deny,allow
	            Allow from all
	    </Directory>
	    
	    Alias /favicon.ico /var/www/project_name/releases/current/project_name/static/favicon.ico
	    
	    # project media
	    Alias /media /var/www/project_name/releases/current/project_name/static
	    <Location "/media">
	            SetHandler None
	    </Location>
	
	    # general admin media
	    Alias /django_admin_media /var/www/project_name/lib/python2.5/site-packages/django/contrib/admin/media
	    <Location "/django_admin_media">
	            SetHandler None
	    </Location>
	
		WSGIDaemonProcess project_name-production user=project_name group=project_name threads=10 python-path=/var/www/project_name/lib/python2.5/site-packages:/var/www/python
		WSGIProcessGroup project_name-production
		WSGIScriptAlias / /var/www/project_name/releases/current/django.wsgi
	
		ErrorLog /var/www/project_name/logs/error.log
		LogLevel warn
		CustomLog /var/www/project_name/logs/access.log combined
	</VirtualHost>

Now create a file called `.gitignore`, containing the following. This
prevents the compiled python code being included in the repository and
the archive we use for deployment. (Add more that you don't want to
publish, e.g. your local settings and development database.)

    *.pyc
    *.pyo
    .tmp*

E.g. here's my default `.gitignore` file:

    *.pyc
    *.pyo
    .tmp*
    .DS_Store
    .project
    .pydevproject
    .settings
    .svn
    secret.txt
    settings_local.py
    dev.db
    build
    *.tar.gz
    *.bak

You should now be ready to initialise a git repository in the top
level project_name directory.

    git init
    git add .gitignore *
    git commit -m "Initial commit"

All of that should leave you with 
    
    project_name/
        .git/
        .gitignore
        requirements.txt
        fabfile.py
        project_name/
            __init__.py
            project_name
            django.wsgi
            manage.py
            settings.py
            urls.py

In reality you might prefer to keep your wsgi files and virtual host files
elsewhere. The fabfile has a variable (config.virtualhost_path) for this case. 
You'll also want to set the hosts that you intend to deploy to (config.hosts)
as well as the user (config.user).

The first task we're interested in is called setup. It installs all the 
required software on the remote machine, then deploys your code and restarts
the webserver.

    fab local setup

_note: Since you can't properly setup the required user and database via fab anyway, 
it may be better to comment the lines calling aptitude._

Here's what I do to create user and database:
(I re-activated the wheel group for sudo-enabled users. That's a potential security risk!)

    adduser --ingroup wheel project_name
    mysql -u root -p
    create user 'project_name'@'localhost' identified by 'password';
    create database proejct_name character set 'utf-8';
    use project_name;
    grant all privileges on project_name.* to 'project_name'@'localhost';
    quit;

After you've made a few changes and commit them to the master Git branch you 
can run to deploy the changes.
    
    fab local deploy

If something is wrong then you can rollback to the previous version.

    fab local rollback
    
Note that this only allows you to rollback to the release immediately before
the latest one. If you want to pick a arbitrary release then you can use the
following, where 20090727170527 is a timestamp for an existing release.

    fab local deploy_version:20090727170527

If you want to ensure your tests run before you make a deployment then you can 
do the following.

    fab local test deploy

"""
from __future__ import with_statement # needed for python 2.5
from fabric.api import *

# globals
env.project_name = 'project_name'
env.use_photologue = False # django-photologue gallery module

# environments

def localhost():
    "Use the local virtual server"
    env.hosts = ['localhost']
    env.user = 'username'
    env.path = '/home/%(user)s/workspace/%(project_name)s' % env
    env.virtualhost_path = env.path

def webserver():
    "Use the actual webserver"
    env.hosts = ['www.example.com']
    env.user = 'username'
    env.path = '/var/www/%(project_name)s' % env
    env.virtualhost_path = env.path
    
# tasks

def test():
    "Run the test suite and bail out if it fails"
    result = local("cd %(path)s; python manage.py test" % env) #, fail="abort")
    
    
def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment
    """
    require('hosts', provided_by=[localhost,webserver])
    require('path')
    sudo('aptitude install -y python-setuptools')
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    sudo('aptitude install -y apache2-threaded')
    sudo('aptitude install -y libapache2-mod-wsgi') # beware, outdated on hardy!
    # we want to get rid of the default apache config
    sudo('cd /etc/apache2/sites-available/; a2dissite default;', pty=True)
    sudo('mkdir -p %(path)s; chown %(user)s:%(user)s %(path)s;' % env, pty=True)
    run('ln -s %(path)s www;' % env, pty=True) # symlink web dir in home
    with cd(env.path):
        run('virtualenv .;' % env, pty=True)
        run('mkdir logs; chmod a+w logs; mkdir releases; mkdir shared; mkdir packages;' % env, pty=True)
        if env.use_photologue: run('mkdir photologue');
        run('cd releases; ln -s . current; ln -s . previous;', pty=True)
    deploy()
    
def deploy():
    """
    Deploy the latest version of the site to the servers, 
    install any required third party modules, 
    install the virtual host and then restart the webserver
    """
    require('hosts', provided_by=[localhost,webserver])
    require('path')
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    upload_tar_from_git()
    install_requirements()
    install_site()
    symlink_current_release()
    migrate()
    restart_webserver()
    
def deploy_version(version):
    "Specify a specific version to be made live"
    require('hosts', provided_by=[localhost,webserver])
    require('path')
    env.version = version
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous;', pty=True)
        run('ln -s %(version)s releases/current' % env, pty=True)
    restart_webserver()
    
def rollback():
    """
    Limited rollback capability. Simple loads the previously current
    version of the code. Rolling back again will swap between the two.
    """
    require('hosts', provided_by=[localhost,webserver])
    require('path')
    with cd(env.path):
        run('mv releases/current releases/_previous;', pty=True)
        run('mv releases/previous releases/current;', pty=True)
        run('mv releases/_previous releases/previous;', pty=True)
    restart_webserver()    
    
# Helpers. These are called by other functions rather than directly

def upload_tar_from_git():
    "Create an archive from the current Git master branch and upload it"
    require('release', provided_by=[deploy, setup])
    local('git archive --format=tar master | gzip > %(release)s.tar.gz' % env)
    run('mkdir -p %(path)s/releases/%(release)s' % env, pty=True)
    put('%(release)s.tar.gz' % env, '%(path)s/packages/' % env)
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env, pty=True)
    local('rm %(release)s.tar.gz' % env)
    
def install_site():
    "Add the virtualhost file to apache"
    require('release', provided_by=[deploy, setup])
    #sudo('cd %(path)s/releases/%(release)s; cp %(project_name)s%(virtualhost_path)s%(project_name)s /etc/apache2/sites-available/' % env)
    sudo('cd %(path)s/releases/%(release)s; cp vhost.conf /etc/apache2/sites-available/%(project_name)s' % env)
    sudo('cd /etc/apache2/sites-available/; a2ensite %(project_name)s' % env, pty=True) 
    
def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    run('cd %(path)s; pip install -E . -r ./releases/%(release)s/requirements.txt' % env, pty=True)
    
def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[deploy, setup])
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous;')
        run('ln -s %(release)s releases/current' % env)
        if env.use_photologue:
            run('cd releases/current/%(project_name)s/static; rm -rf photologue; ln -s %(path)s/photologue;' % env, pty=True)
    
def migrate():
    "Update the database"
    require('project_name')
    run('cd %(path)s/releases/current/%(project_name)s;  ../../../bin/python manage.py syncdb --noinput' % env, pty=True)
    
def restart_webserver():
    "Restart the web server"
    sudo('/etc/init.d/apache2 reload', pty=True)
