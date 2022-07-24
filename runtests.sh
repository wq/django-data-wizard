#!/bin/bash

set -e

if [ "$CELERY" ]; then
    celery worker -A tests &
fi;

python -m django test --settings=tests.settings
