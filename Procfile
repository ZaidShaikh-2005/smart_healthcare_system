web: python manage.py migrate && python manage.py load_symptoms && gunicorn soloRising.wsgi:application --bind 0.0.0.0:$PORT
