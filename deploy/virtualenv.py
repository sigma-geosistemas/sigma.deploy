"""Tasks related to creating and maintenance of virtualenvs"""
from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.operations import sudo
from fabric.state import env


@task
def create_virtualenvs_folder():
    """Create our folder to hold
    all of our machine virtualenvs"""
    if not exists(env.virtualenvs_path):

        sudo("mkdir -p {0}".format(env.virtualenvs_path), shell=False)

@task
def create_virtualenv():
    """
    Creates a new virtualenv
    """

    virtualenv_name = env.get("virtualenv_name", None)

    if not virtualenv_name:
        raise ValueError("We need the virtualenv_name variable to create the virtualenv")

    if not exists(env.virtualenvs_path):
        create_virtualenvs_folder()

    with cd(env.virtualenvs_path):
        if not exists(env.virtualenv_path):
            sudo("virtualenv {0}".format(virtualenv_name))