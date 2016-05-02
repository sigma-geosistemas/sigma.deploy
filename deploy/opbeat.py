from fabric.api import runs_once, lcd, local, task
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
    with(lcd(path)):
        revision = local('git log -n 1 --pretty="format:%H"', capture=True)
        branch = local('git rev-parse --abbrev-ref HEAD', capture=True)
        local('curl https://intake.opbeat.com/api/v1/organizations/{}/apps/{}/releases/'
              ' -H "Authorization: Bearer {}"'
              ' -d rev={}'
              ' -d branch={}'
              ' -d status=completed'.format(org, app, secret, revision, branch))
