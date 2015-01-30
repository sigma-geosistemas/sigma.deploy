import os
from fabric.contrib.files import upload_template, exists
from fabric.decorators import task
from fabric.operations import sudo
from fabric.state import env


@task
def write_nginx_conf():

    ctx = { "allowed_hosts": env.django["allowed_hosts"],
            "app_root": env.source_root,
            "media_root": env.django["media_root"],
            "static_root": env.django["static_root"] }

    if env.has_key("django_admin_enabled") and env.django_admin_enabled:

        ctx["django_admin_enabled"] = True

        ctx["admin_contrib"] = env.django["django_contrib_path"]

    if exists("/etc/nginx/sites-enabled/default"):
        sudo("rm -rf /etc/nginx/sites-enabled/default")

    upload_template(filename="webserver/nginx.template",
                    destination="/etc/nginx/sites-enabled/{0}.conf".format(env.virtualenv_name),
                    use_jinja=True,
                    template_dir=env.deploy_templates_path,
                    use_sudo=True,
                    context=ctx,
                    backup=False)


@task
def write_webserver_command():

    ctx = {"virtualenv_name": env.virtualenv_name,
           "app_root": env.source_root,
           "virtualenv_path": os.path.join(env.virtualenv_path, "bin"),
           "app_path": env.app_path,
           "app_user": env.app_user,
           "app_group": env.app_group,
           "no_workers": env.no_workers}

    upload_template(filename="webserver/start_webserver.template",
                    destination=os.path.join(env.app_path, "start_webserver.sh"),
                    use_jinja=True,
                    template_dir=env.deploy_templates_path,
                    use_sudo=True,
                    context=ctx,
                    backup=False)

    sudo("chmod +x {0}".format(os.path.join(env.app_path, "start_webserver.sh")))

@task
def write_supervisor_conf():

    ctx = {"virtualenv_name": env.virtualenv_name,
           "command_path": os.path.join(env.app_path, "start_webserver.sh"),
           "app_user": env.app_user,
           "app_path": env.app_path}

    upload_template(filename="webserver/supervisor.template",
                    destination="/etc/supervisor/conf.d/{0}.conf".format(env.virtualenv_name),
                    use_jinja=True,
                    template_dir=env.deploy_templates_path,
                    use_sudo=True,
                    context=ctx,
                    backup=False)