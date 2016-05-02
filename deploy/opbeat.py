from fabric.api import runs_once, lcd, local, task

@task
@runs_once
def register_deployment(git_path):

    with(lcd(git_path)):
        org = env.opbeat.
        app = ""
        token = ""
        revision = local('git log -n 1 --pretty="format:%H"', capture=True)
        branch = local('git rev-parse --abbrev-ref HEAD', capture=True)
        local('curl https://intake.opbeat.com/api/v1/organizations/{}/apps/{}/releases/'
              ' -H "Authorization: Bearer {}"'
              ' -d rev={}'
              ' -d branch={}'
              ' -d status=completed'.format(org, app, token, revision, branch))
