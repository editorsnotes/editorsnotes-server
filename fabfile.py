raise EnvironmentError("Fabric is no longer used to issue management commands")

@task
def sync_database():
    "Sync db, make cache tables, and run South migrations"
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
