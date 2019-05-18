from fabric.decorators import task
from fabric.operations import sudo, run


@task
def git_pull():
    """
    Updates the repository
    """
    run("cd /root/dev/collection_backend && git pull origin master")


# @task
# def celery_logs():
#     """
#     Updates the repository
#     """
#     sudo("tail -f /var/log/celery/belka.log")


@task
def update_supervisor():
    """
        Dunno for now (
    """
    # sudo("cp ~/{}/configs/supervisor/celery.conf /etc/supervisor/conf.d".format(env.repo_name))
    # sudo("supervisorctl reread; supervisorctl restart celery; supervisorctl restart celerybeat; supervisorctl restart flower; supervisorctl update; supervisorctl status celery")
    sudo("supervisorctl update")


@task
def update():
    """
    Restarts the server
    """
    run("cd /root/dev/collection_backend/ && . ./run.sh")
    sudo("systemctl restart gunicorn")
    sudo("systemctl restart nginx")
    update_supervisor()
