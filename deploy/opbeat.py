from fabric.api import runs_once, local, task
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
    with(cd(path)):
        revision = local('git log -n 1 --format:oneline', capture=True).split(" ")[0]
        branch = local('git rev-parse --abbrev-ref HEAD', capture=True)
        local('curl https://intake.opbeat.com/api/v1/organizations/{}/apps/{}/releases/'
              ' -H "Authorization: Bearer {}"'
              ' -d rev={}'
              ' -d branch={}'
              ' -d status=completed'.format(org, app, secret, revision, branch))
