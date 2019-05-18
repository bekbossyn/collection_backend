from . import common

from fabric.state import env
from fabric.decorators import task

env.repository = "https://github.com/bekbossyn/collection_backend.git"
env.repo_name = "collection_backend"
env.hosts = ["188.166.13.81"]
env.user = "root"
env.password = "Truesight7"


# @task
# def telecom():
#     env.user = "dev"
#     env.password = "root"
#     env.hosts = ["185.22.67.213"]

#
# @task
# def ocean():
#     env.user = "root"
#     env.password = "Truesight7"
#     env.hosts = ["159.65.203.197"]
#
#     run("cd /root/belka && git pull origin master")
#

@task
# @hosts(['159.65.203.197'])
def restart():
    """
        updates the repo, restarts the server
    """
    common.git_pull()
    common.update()
