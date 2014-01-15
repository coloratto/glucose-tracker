from fabric.api import local, env, cd, sudo


env.hosts = ['www.glucosetracker.net']

# The user account that owns the application files and folders.
owner = 'glucosetracker'

app_name = 'glucosetracker'
settings_file = 'settings.production'


def prepare_deployment():
    local('coverage run manage.py test -v 2')


def deploy():
    """
    Deploy the app to the remote host.

    Steps:
        1. Change to the app's directory.
        2. Pull changes from master branch in git.
        3. Activate virtualenv.
        4. Run pip install using the requirements.txt file.
        5. Run South migrations.
        6. Run tests.
        7. Restart gunicorn WSGI server using supervisor.
    """
    with cd('/webapps/glucosetracker/glucose-tracker'):

        sudo('git pull', user=owner)

        venv_command = 'source ../bin/activate'

        pip_command = 'pip install -r requirements.txt'
        sudo('%s && %s' % (venv_command, pip_command), user=owner)

        south_command = 'python glucosetracker/manage.py migrate --all ' \
                        '--settings=%s' % settings_file
        sudo('%s && %s' % (venv_command, south_command), user=owner)

        coverage_command = 'coverage run --source=. glucosetracker/manage.py ' \
                           'test -v 2'
        sudo('%s && %s' % (venv_command, coverage_command), user=owner)

        sudo('supervisorctl restart glucosetracker')