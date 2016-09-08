set -e
if [ "$LINT" ]; then
    flake8 data_wizard tests --exclude migrations
    flake8 data_wizard/migrations --ignore E501
else
    export DJANGO_SETTINGS_MODULE=tests.swap_settings
    python -c "import tests"
    celery worker -A tests &
    python setup.py test
fi
