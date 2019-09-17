#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "baskervilleweb.settings")

    from django.core.management import execute_from_command_line

    argv=sys.argv
    has_port=False
    for arg in argv:
        if arg.endswith("manage.py"): continue
        if arg=="runserver": continue
        if arg.startswith("-"): 
            continue
        has_port=True
        break
    if not has_port:
        argv.append("8001")

    
    execute_from_command_line(sys.argv)
