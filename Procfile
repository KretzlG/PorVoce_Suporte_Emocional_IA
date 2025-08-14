release: export FLASK_APP=wsgi.py && flask db upgrade
web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 wsgi:app
