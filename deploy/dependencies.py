import os
from fabric.context_managers import cd
from fabric.contrib.files import exists, append
from fabric.decorators import task
from fabric.operations import sudo
from fabric.state import env
import fabtools
from fabtools.files import is_file
from fabtools.git import checkout, clone
from fabtools.python import is_pip_installed, install_pip, virtualenv
from fabtools.python import install_requirements as fab_install_requirements
from .database import configure_database_access, create_databases
from .django import write_local_settings, migrate, collectstatic
from .packages import MINIMAL_PACKAGES, POSTGRESQL_PACKAGES, POSTGIS_PACKAGES
from .system import create_application_folder
from .virtualenv import create_virtualenv

POSTGRESQL_APT_REPOSITORY_URL = "http://apt.postgresql.org/pub/repos/apt/"

# selects a postgresql version to install.
POSTGRESQL_VERSION = env.get("postgresql_version", "9.5")

# selects which postgis version to install
POSTGIS_VERSION = env.get("postgis_version", "2.3")

POSTGRESQL_UTOPIC_REPO = "utopic-pgdg"
POSTGRESQL_TRUSTY_REPO = "trusty-pgdg"
POSTGRESQL_PRECISE_REPO = "precise-pgdg"
POSTGRESQL_LUCID_REPO = "lucid-pgdg"
POSTGRESQL_XENIAL_REPO = "xenial-pgdg"

POSTGRESQL_REPOSITORIES = {"utopic": POSTGRESQL_UTOPIC_REPO,
                           "trusty": POSTGRESQL_TRUSTY_REPO,
                           "precise": POSTGRESQL_PRECISE_REPO,
                           "lucid": POSTGRESQL_LUCID_REPO,
                           "xenial": POSTGRESQL_XENIAL_REPO}

SRID_900913_DEFINITION = "<900913> proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over<>"  # noqa
SRID_900913_WKT_DEFINITION = """900913,PROJCS["Google Maps Global Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_2SP"],PARAMETER["standard_parallel_1",0],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],AUTHORITY["EPSG","900913"]]"""  # noqa
EPSG_SHARED = "/usr/share/proj/epsg"
EPSG_LOCAL = "/usr/local/share/proj/epsg"


def _determine_postgresql_repository(distro):

    if distro not in POSTGRESQL_REPOSITORIES:
        raise ValueError("Distro not supported! Valid distros are: {0}".format(", ".join(POSTGRESQL_REPOSITORIES.keys())))

    return POSTGRESQL_REPOSITORIES[distro]


@task
def configure_srid_900913():

    if is_file(EPSG_SHARED, use_sudo=True):

        append(EPSG_SHARED, SRID_900913_DEFINITION, use_sudo=True)

    if is_file(EPSG_LOCAL, use_sudo=True):

        append(EPSG_LOCAL, SRID_900913_DEFINITION, use_sudo=True)

    data_dir = sudo('gdal-config --datadir')
    cubewerx = os.path.join(data_dir, 'cubewerx_extra.wkt')
    append(cubewerx, SRID_900913_WKT_DEFINITION, use_sudo=True)


@task
def install_minimal():

    """Installs minimal dependencies"""

    sudo("apt-get update")
    sudo("apt-get install --yes --force-yes {0}".format(MINIMAL_PACKAGES), False)

    if env.get("extra_packages"):
        sudo("apt-get install --yes --force-yes {0}".format(env.extra_packages), False)


@task
def install_nodejs():

    if env.get("node_support"):
        fabtools.nodejs.install_from_source()
        fabtools.nodejs.install_package('bower')


@task
def install_postgresql():

    """Installs PostgreSQL. Oh really? :P"""

    distro = env.get("ubuntu-distro", "xenial")
    repository = _determine_postgresql_repository(distro)

    sudo('echo "deb {0} {1} main" > /etc/apt/sources.list.d/pgdg.list'.format(POSTGRESQL_APT_REPOSITORY_URL, repository))
    sudo("wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -")
    sudo("apt-get update")

    packages = POSTGRESQL_PACKAGES.format(POSTGRESQL_VERSION)
    sudo("apt-get install --yes --force-yes {0}".format(packages))

@task
def install_language_pack():

    sudo("apt-get install --yes --force-yes language-pack-pt")

@task
def install_postgis():

    packages = POSTGIS_PACKAGES.format(POSTGRESQL_VERSION, POSTGIS_VERSION)
    sudo("apt-get install --yes --force-yes {0}".format(packages))


@task
def clone_repository():
    if not exists(os.path.join(env.app_root, "requirements.txt")):
        clone(env.git_url, env.app_root, use_sudo=True)

    if 'deploy_branch' in env:
        checkout(env.app_root, env.deploy_branch, use_sudo=True)


@task
def install_requirements():

    """Installs all the requirements on the requirements file"""

    REQUIREMENTS_DICT = {"SINGLE": "requirements.txt",
                         "PRODUCTION": "requirements/production.txt",
                         "TEST": "requirements/tests.txt",
                         "LOCAL": "requirements/local.txt"}

    if not is_pip_installed():
        install_pip()  # use_sudo defaults to True

    # inside here we check if the virtualenv exists, no need for double check.
    create_virtualenv()

    create_application_folder()
    if env.clone.upper() == 'TRUE':
        clone_repository()

    with virtualenv(env.virtualenv_path):
        with cd(env.app_root):

            env_type = env.get("environment-type", "LOCAL")

            fab_install_requirements(REQUIREMENTS_DICT[env_type],
                                     use_sudo=True)


@task
def upgrade_requirements():

    """upgrades all the requirements. basically a pip install -U -r"""

    with virtualenv(env.virtualenv_path):
        with cd(env.app_root):
            fab_install_requirements("requirements.txt",
                                     upgrade=True,
                                     use_sudo=True)


@task
def install_all():

    """Install all dependencies"""
    install_language_pack()
    install_minimal()
    install_postgresql()
    install_postgis()
    install_requirements()


@task
def configure_all():

    configure_srid_900913()
    configure_database_access()
    create_databases()
    write_local_settings()
    migrate()
    collectstatic()


@task
def install_and_config():

    install_all()
    configure_all()