"""All tasks related to database manipulation"""
from fabric.context_managers import settings
from fabric.decorators import task
from fabric.operations import run, sudo
from fabric.state import env
from fabtools import user as system_user
from fabtools.postgres import database_exists as postgresql_exists, user_exists
from fabtools.postgres import create_database as create_postgres
from fabtools.postgres import _run_as_pg
from fabtools.mysql import database_exists as mysql_exists
from fabtools.mysql import create_database as create_mysql

@task
def configure_database_access():

    configure_postgres_user()
    configure_postgres_role()

@task
def configure_postgres_user():

    if system_user.exists("postgres"):
        system_user.modify("postgres", password=env.postgresql_user_password)

@task
def configure_postgres_role():

    if user_exists("postgres"):
        _run_as_pg("psql -U postgres -c \"ALTER USER postgres WITH password '{0}'\"".format(env.postgresql_role_password))


@task
def create_databases():

    databases = env.get("databases", None)

    if not databases:
        raise ValueError("We have no databases configuration.")

    database_creator = DatabaseCreator()
    database_creator.create_databases(databases)


class DatabaseCreator(object):

    DATABASE_ENGINE_MAPPING = {"django.contrib.gis.db.backends.postgis": "_create_database_postgis",
                               "django.db.backends.postgresql_psycopg2": "_create_database_postgresql",
                               "django.db.backends.sqlite3": "_create_database_sqlite3",
                               "django.db.backends.mysql": "_create_database_mysql",
                               "django.db.backends.oracle": "_create_database_oracle"}

    POSTGIS_EXTENSION_COMMAND = 'psql -U postgres -d {0} -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"'
    DROP_DATABASE_COMMAND = 'psql -U postgres -c "DROP DATABASE IF EXISTS {0};"'

    def __init__(self):

        pass

    def create_databases(self, databases):

        """Given a env.databases setting, creates all necessary databases"""

        for database_alias in databases:

            database = databases[database_alias]

            if not database["MANAGED"]:
                continue

            if not database["ENGINE"] in self.DATABASE_ENGINE_MAPPING:
                raise ValueError("Database engine not supported.")

            method = getattr(self, self.DATABASE_ENGINE_MAPPING[database["ENGINE"]])
            method(database)

    def _create_database_postgresql(self, database_settings):

        if not postgresql_exists(database_settings["NAME"]):
            result = create_postgres(name=database_settings["NAME"],
                                     owner=database_settings["USER"])

            return result

    def _create_database_postgis(self, database_settings):

        self._create_database_postgresql(database_settings)

        major_postgis_version = int(env.get("postgis_version").split(".")[0])

        if major_postgis_version < 2:
            raise ValueError("PostGIS versions minor then 2 are not supported.")

        with settings(warn_only=True):
            result = _run_as_pg(self.POSTGIS_EXTENSION_COMMAND.format(database_settings["NAME"]))

            if result.failed:
                _run_as_pg(self.DROP_DATABASE_COMMAND.format(database_settings["NAME"]))

    def _create_database_sqlite3(self, database_settings):
        print "Database not created using fabric. It will be created using migrations."

    def _create_database_mysql(self, database_settings):

        if not mysql_exists(database_settings["NAME"]):
            create_mysql(name=database_settings["NAME"],
                         owner=database_settings["USER"],
                         owner_host=database_settings["HOST"])

    def _create_database_oracle(self, database_settings):
        print "Oracle database creation not implemented yet."