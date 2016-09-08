set -e
if [ "$LINT" ]; then
    flake8 data_wizard tests --exclude migrations
    flake8 data_wizard/migrations --ignore E501
else
    export DJANGO_SETTINGS_MODULE=tests.swap_settings
    python3 -c "import tests"
    celery worker -A tests --purge &
    python3 setup.py test
fi
