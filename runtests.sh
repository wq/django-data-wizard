set -e
if [ "$LINT" ]; then
    flake8 data_wizard tests --exclude migrations
    flake8 data_wizard/migrations --ignore E501
else
    python -c "import tests"
    celery worker -A tests &
    python setup.py test
fi
