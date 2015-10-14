#!/usr/bin/env python
import os, sys

if __name__ == "__main__":
    settings_module = (
        'editorsnotes.settings_test'
        if len(sys.argv) > 1 and sys.argv[1] == 'test'
        else 'editorsnotes.settings')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
