import os

os.system('python3 ./workers.py &')
os.system("gunicorn --bind=0.0.0.0 --workers=5 --timeout 800 app:app --access-logfile '-' --error-logfile '-'")
