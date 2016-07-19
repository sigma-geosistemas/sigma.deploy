from fabric.api import runs_once, local, task, run
from fabric.context_managers import cd
from fabric.state import env


@task
@runs_once
def register_deployment(path, org, app, secret):
    """
    command example
    fab register_deployment:path="<path>",
                               org=<org>,
                               app=<app>,
                               secret=<secret>
    """
    with cd(path):
        revision = run('git log -n 1 --format=%H')
        branch = run('git rev-parse --abbrev-ref HEAD')
        run('''curl https://intake.opbeat.com/api/v1/organizations/{0}/apps/{1}/releases/ \ 
-H "Authorization: Bearer {2}" \
-d rev={3} \
-d branch={4} \
-d status=completed'''.format(org, app, secret, revision, branch))
