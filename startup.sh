#!/usr/bin/env bash

# <module> is the folder that contains wsgi.py. If you need to use a subfolder,
# specify the parent of <module> using --chdir.

python3 ./workers.py &
#gunicorn --bind=0.0.0.0 --workers=3 --timeout 800 app:app --access-logfile '-' --error-logfile '-'
gunicorn --bind=0.0.0.0 --workers=3 --timeout 800 app:app