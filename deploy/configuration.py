import ConfigParser
import os
import pprint
from fabric.state import env
from fabric.decorators import task

@task
def load_fabconfig(configuration_file=None):

    if configuration_file:
        configuration = ConfigParser.RawConfigParser()
        configuration.read(configuration_file)

        _load_main_configuration(configuration)
        _load_deploy_configuration(configuration)
        _load_os_configuration(configuration)
        _load_databases_configuration(configuration)
        _load_packages_configuration(configuration)
        _load_django_configuration(configuration)

    print "Configuration Done!"
    pprint.pprint(env, indent=2)

def _load_main_configuration(configuration):

    # /opt/apps
    env.app_folder_prefix = configuration.get("main", "app_folder_prefix")

    # mapport
    env.virtualenv_name = configuration.get("main", "virtualenv_name")

    # /opt/apps/.virtualenvs
    env.virtualenvs_path = os.path.join(env.app_folder_prefix, configuration.get("main", "virtualenvs_path"))

    # /opt/apps/.virtualenvs/mapport
    env.virtualenv_path = os.path.join(env.virtualenvs_path, env.virtualenv_name)

    # /opt/apps/mapport
    env.app_path = os.path.join(env.app_folder_prefix, env.virtualenv_name)

    # /opt/apps/mapport/mapport
    env.app_root = os.path.join(env.app_path, env.repository_name)
    env.django_settings_path = os.path.join(env.app_root, env.virtualenv_name)

def _load_git_configuration(configuration):

    # http://github.com/enplan/mapport.git
    env.git_url = configuration.get("git", "git_url")

    # mapport
    env.repository_name = configuration.get("git", "repository_name")

    if configuration.has_option("git", "source_root"):
        # /opt/apps/mapport/mapport/src
        env.source_root = os.path.join(env.app_root, configuration.get("git", "source_root"))
        env.django_settings_path = os.path.join(env.source_root, env.virtualenv_name)


    if configuration.has_option("git", "deploy_branch"):
        # ci-george, for example
        env.deploy_branch = configuration.get("git", "deploy_branch")


def _load_packages_configuration(configuration):

    env.postgresql_version = configuration.get("packages", "postgresql_version")

    env.postgis_version = configuration.get("packages", "postgis_version")

    if configuration.has_section("packages") and configuration.has_option("packages", "extra_packages"):
        env.extra_packages = configuration.get("packages", "extra_packages")

def _load_os_configuration(configuration):

    """Loads all OS configurations"""

    # trusty
    env.distro = configuration.get("os", "distro")

def _load_deploy_configuration(configuration):

    """Load deploy related configurations"""

    first_task = env.tasks[0]

    if configuration.has_section("deploy") and first_task != "vagrant":

        if configuration.has_option("deploy", "fabric_user"):
            env.user = configuration.get("deploy", "fabric_user")

        if configuration.has_option("deploy", "fabric_sudo_user"):
            env.sudo_user = configuration.get("deploy", "fabric_sudo_user")

        if configuration.has_option("deploy", "fabric_sudo_password"):
            env.password = configuration.get("deploy", "fabric_sudo_password")

        if configuration.has_option("deploy", "fabric_parallel"):
            env.parallel = configuration.getboolean("deploy", "fabric_parallel")

        if configuration.has_option("deploy", "fabric_hosts"):
            env.hosts = configuration.get("deploy", "fabric_hosts")

    env.deploy_templates_path = configuration.get("deploy", "deploy_templates_path")

    env.postgresql_user_password = configuration.get("deploy", "postgresql_user_password")
    env.postgresql_role_password = configuration.get("deploy", "postgresql_role_password")

    env.app_user = configuration.get("deploy", "app_user")
    env.app_group = configuration.get("deploy", "app_group")
    env.no_workers = configuration.get("deploy", "no_workers")


def _load_databases_configuration(configuration):

    """Load all databases defined in the configuration file to environment in fabric.
    The configuration variable must be the result of ConfigParse.read method object."""

    env.databases = {}

    for section in configuration.sections():

        if section.startswith("database-"):

            try:
                alias = section.split("-")[1]
            except:
                raise ValueError("Malformed database configuration. {0} should have the prefix database- followed by the name of the django alias.")

            try:
                database_engine = configuration.get(section, "engine")
                database_name = configuration.get(section, "name")
                database_host = configuration.get(section, "host")
                database_port = configuration.get(section, "port")
                database_user = configuration.get(section, "user")
                database_password = configuration.get(section, "password")
                database_options = None
                if configuration.has_option(section, "managed"):
                    database_managed = configuration.getboolean(section, "managed")
                else:
                    database_managed = True

                if configuration.has_option(section, "options"):
                    database_options = configuration.get(section, "options")

            except ConfigParser.NoOptionError:
                raise ValueError("Missing option in the database configuration for PostgreSQL.")

            env.databases[alias] = {"ENGINE": database_engine,
                                    "NAME": database_name,
                                    "USER": database_user,
                                    "PASSWORD": database_password,
                                    "HOST": database_host,
                                    "PORT": database_port,
                                    "MANAGED": database_managed}

            if database_options:
                env.databases[alias]["OPTIONS"] = database_options

def _load_django_configuration(configuration):

    env.django = {}

    env.django["debug"] = configuration.getboolean("django", "debug")

    env.django["template_debug"] = configuration.getboolean("django", "template_debug")
    if configuration.has_option("django", "allowed_hosts"):
        env.django["allowed_hosts"] = configuration.get("django", "allowed_hosts")
    else:
        env.django["allowed_hosts"] = None

    if configuration.has_option("django", "media_root"):
        env.django["media_root"]  = configuration.get("django", "media_root")
    else:
        env.django["media_root"] = os.path.join(env.source_root, "{0}_website".format(env.virtualenv_name), "media")

    if configuration.has_option("django", "static_root"):
        env.django["static_root"] = configuration.get("django", "static_root")
    else:
        env.django["static_root"] = os.path.join(env.source_root, "{0}_website".format(env.virtualenv_name), "static")

    env.django["django_admin_enabled"] = configuration.getboolean("django", "django_admin_enabled")

    if env.django["django_admin_enabled"]:

        env.django["django_contrib_path"] = os.path.join(env.virtualenv_path, "lib/python2.7/site-packages/django/contrib")