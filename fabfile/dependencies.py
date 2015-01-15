import os
from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.operations import sudo
from fabric.state import env
from fabtools.git import checkout, clone
from fabtools.python import is_pip_installed, install_pip, virtualenv
from fabtools.python import install_requirements as fab_install_requirements
from .packages import MINIMAL_PACKAGES, POSTGRESQL_PACKAGES, POSTGIS_PACKAGES
from .system import create_application_folder
from .virtualenv import create_virtualenv

POSTGRESQL_APT_REPOSITORY_URL = "http://apt.postgresql.org/pub/repos/apt/"

# selects a postgresql version to install.
POSTGRESQL_VERSION = env.get("postgresql_version", "9.3")

# selects which postgis version to install
POSTGIS_VERSION = env.get("postgis_version", "2.1")

POSTGRESQL_UTOPIC_REPO = "utopic-pgdg"
POSTGRESQL_TRUSTY_REPO = "trusty-pgdg"
POSTGRESQL_PRECISE_REPO = "precise-pgdg"
POSTGRESQL_LUCID_REPO = "lucid-pgdg"

POSTGRESQL_REPOSITORIES = {"utopic": POSTGRESQL_UTOPIC_REPO,
                           "trusty": POSTGRESQL_TRUSTY_REPO,
                           "precise": POSTGRESQL_PRECISE_REPO,
                           "lucid": POSTGRESQL_LUCID_REPO}

def _determine_postgresql_repository(distro):

    if distro not in POSTGRESQL_REPOSITORIES:
        raise ValueError("Distro not supported! Valid distros are: {0}".format(", ".join(POSTGRESQL_REPOSITORIES.keys())))

    return POSTGRESQL_REPOSITORIES[distro]


@task
def install_minimal():

    """Installs minimal dependencies"""

    sudo("apt-get update")
    sudo("apt-get install --yes --force-yes {0}".format(MINIMAL_PACKAGES))

    if env.get("extra_packages"):
        sudo("apt-get install --yes --force-yes {0}".format(env.extra_packages))

@task
def install_postgresql():

    """Installs PostgreSQL. Oh really? :P"""

    distro = env.get("ubuntu-distro", "trusty")
    repository = _determine_postgresql_repository(distro)

    sudo('echo "deb {0} {1} main" > /etc/apt/sources.list.d/pgdg.list'.format(POSTGRESQL_APT_REPOSITORY_URL, repository))
    sudo("wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -")
    sudo("apt-get update")

    packages = POSTGRESQL_PACKAGES.format(POSTGRESQL_VERSION)
    sudo("apt-get install --yes --force-yes {0}".format(packages))

@task
def install_postgis():

    packages = POSTGIS_PACKAGES.format(POSTGRESQL_VERSION, POSTGIS_VERSION)
    sudo("apt-get install --yes --force-yes {0}".format(packages))

@task
def clone_repository():
    if not exists(os.path.join(env.app_root, "requirements.txt")):
        clone(env.git_url, env.app_root, use_sudo=True)

    if env.has_key("deploy_branch"):
        checkout(env.app_root, env.deploy_branch, use_sudo=True)
@task
def install_requirements():

    """Installs all the requirements on the requirements file"""

    # TODO: sudo should not be required. we need to configure this to use a new user for each app.

    if not is_pip_installed():
        install_pip() # use_sudo defaults to True

    # inside here we check if the virtualenv exists, no need for double check.
    create_virtualenv()

    create_application_folder()

    clone_repository()

    with virtualenv(env.virtualenv_path):
        with cd(env.app_root):
            fab_install_requirements("requirements.txt", use_sudo=True)

@task
def upgrade_requirements():

    """upgrades all the requirements. basically a pip install -U -r"""

    with virtualenv(env.virtualenv_path):
        with cd(env.app_root):
            fab_install_requirements("requirements.txt", upgrade=True, use_sudo=True)

@task
def install_all():

    """Install all dependencies"""

    install_minimal()
    install_postgresql()
    install_postgis()
    install_requirements()