"""System tasks, such as creation of folders,
setting up users, etc."""
import os
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.operations import sudo, local
from fabric.state import env


@task
def create_application_folder():

    app_folder_prefix = env.get("app_folder_prefix", None)
    virtualenv_name = env.get("virtualenv_name", None)
    if not virtualenv_name:
        raise ValueError("We need the virtualenv_name variable to create the application folder.")

    app_folder = None

    if app_folder_prefix:
        app_folder = os.path.join(app_folder_prefix, virtualenv_name)
    else:
        app_folder = virtualenv_name

    if not exists(app_folder):
        sudo("mkdir -p {0}".format(app_folder), shell=False)