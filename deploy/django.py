from fabric.context_managers import cd
from fabric.contrib.files import upload_template, exists
from fabric.decorators import task
from fabric.operations import sudo, os, run
from fabric.state import env
from fabtools.git import checkout
from fabtools.python import virtualenv


@task
def write_local_settings():

    """Write a local_settings file to our settings folder."""

    if not env.has_key("deploy_templates_path"):

        print "Its not possible to writeoff localsettings because we can't locate our deploy templates"
        return

    ctx = { "databases": env.databases,
            "debug": str(env.django["debug"]),
            "template_debug": str(env.django["template_debug"]),
            "media_root": env.django["media_root"],
            "static_root": env.django["static_root"]}

    if env.django["allowed_hosts"]:
        ctx["allowed_hosts"] = env.django["allowed_hosts"].split(",")

    upload_template(filename=os.path.join(env.deploy_templates_path, "django/local_settings.template"),
                    destination=os.path.join(env.django_settings_path, "local_settings.py"),
                    use_jinja=True,
                    template_dir=env.deploy_templates_path,
                    use_sudo=True,
                    context=ctx,
                    backup=False)

    if not exists(env.django["media_root"]):
        sudo("mkdir -p {0}".format(env.django["media_root"]))

    if not exists(env.django["static_root"]):
        sudo("mkdir -p {0}".format(env.django["static_root"]))

@task
def migrate():

    """Executes all the migrations"""

    with virtualenv(env.virtualenv_path):

        with cd(env.source_root):
            run("./manage.py migrate")

@task
def runserver():

    """Starts the default django server"""

    with virtualenv(env.virtualenv_path):

        with cd(env.source_root):
            sudo("./manage.py runserver 0.0.0.0:8000")

@task
def collectstatic():

    with virtualenv(env.virtualenv_path):

        with cd(env.source_root):
            sudo ("./manage.py collectstatic --noinput")

@task
def run_tests():

    """Run all tests for the project"""

    with virtualenv(env.virtualenv_path):

        if env.has_key("deploy_branch"):
            checkout(env.app_path, env.deploy_branch)

        with cd(env.source_root):
            sudo("./manage.py test")