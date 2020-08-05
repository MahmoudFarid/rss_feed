RSS Scraper App
===============

A django rest app for rss scraper.


Setting Up Development Environment
----------------------------------

Using Docker
^^^^^^^^^^^^

* Docker; if you don’t have it yet, follow the installation_instructions_.
.. _installation_instructions: https://docs.docker.com/install/#supported-platforms

* Docker Compose; refer to the official documentation for the installation_guilde_.
.. _installation_guilde: https://docs.docker.com/compose/install/


Then you can build the environment, this can take a while especially the first time you run this particular command on your development system:

    $ make build

That's it!

To run server normally at anytime, just run this command:

    $ make up

To build the app then run server:

    $ make upbuild

To open bash or excute any manage.py commands:

    $ make bash

To create superuser:

    $ make createsuperuser

To make fast migration instead of opening bash:

    $ make makemigrations

    $ make migrate

To run unittests (with running django container):

    $ make test_local

To run unittests (without running django container):

    $ make test

To allow debugging in development with ipdb, run server with this command:

    $ make debug django


Running Locally
^^^^^^^^^^^^^^^

1- create a virtualenv.

2- Activate the virtualenv you have just created.

3- Install development requirements:

    $ pip install -r requirements/local.txt

4- Configure your DB, to make it easily you can change the DB to be sqlite3 instead of postgresql Django Doc.
.. https://docs.djangoproject.com/en/2.0/ref/settings/#s-databases

5- Apply Migrations

    $ ./manage.py migrate

6- Run server

    $ ./manage.py runserver
