raise EnvironmentError("Fabric is no longer used to issue management commands")

@task
def sync_database():
    "Sync db, make cache tables, and run South migrations"

    new_installation = len(get_db_tables()) == 0

    with lcd(PROJ_ROOT):
        create_cache_tables()
        local('{python} manage.py migrate --noinput'.format(**env))

    if new_installation:
        print('\nDatabase synced. Follow prompts to create an initial '
              'super user and project.')
        username = prompt('Username: ', validate=str)
        local('{python} manage.py createsuperuser --username {username}'.format(
            username=username, **env))

        project_name = prompt('Project name (blank to skip): ')
        if project_name:
            project_slug = prompt('Project slug: ', validate=str)

            local('{python} manage.py createproject '
                  '"{name}" {slug} --users={username}'.format(
                      name=project_name, slug=project_slug,
                      username=username, **env))

@task
def create_cache_tables():
    caches = ['zotero_cache']
    tables = get_db_tables()
    for cache in caches:
        if "'{}'".format(cache) in tables:
            continue
        with lcd(PROJ_ROOT):
            local('{python} manage.py createcachetable {cache}'.format(cache=cache, **env))


ADMIN_CSS_IN = './editorsnotes/auth/static/admin.css'
ADMIN_CSS_OUT = './static/admin_compiled.css'
ADMIN_CSS_OUT_DEV = ADMIN_CSS_IN.replace('.css', '_compiled.css')

@task
def compile_admin_css():
    with lcd(PROJ_ROOT):
        local('./node_modules/.bin/cssnext {} {}'.format(
            ADMIN_CSS_IN, ADMIN_CSS_OUT))

@task
def watch_admin_css():
    with lcd(PROJ_ROOT):
        local('./node_modules/.bin/cssnext --watch --verbose {} {}'.format(
            ADMIN_CSS_IN, ADMIN_CSS_OUT_DEV))

def get_db_tables():
    tables = local('{python} manage.py inspectdb | '
                   'grep "db_table =" || true'.format(**env), capture=True)
    return tables or []

def make_virtual_env():
    "Make a virtual environment for local dev use"
    with lcd(PROJ_ROOT):
        local('virtualenv -p python2 .')
        local('./bin/pip install -r requirements.txt')

def collect_static():
    with lcd(PROJ_ROOT):
        local('{python} manage.py collectstatic --noinput -v0'.format(**env))

def generate_secret_key():
    SECRET_CHARS = 'abcdefghijklmnopqrstuvwxyz1234567890-=!@#$%^&*()_+'
    return ''.join([random.choice(SECRET_CHARS) for i in range(50)])
