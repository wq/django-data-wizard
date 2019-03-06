#!/bin/bash

set -e

if [ "$CELERY" ]; then
    celery worker -A tests &
fi;

python3 -m django runserver --settings=tests.settings
