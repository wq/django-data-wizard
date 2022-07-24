#!/usr/bin/env bash
# set -e

# find package name in pyproject.toml:
# grep -E 'name\s*=\s*["'"'].*['"'"]' pyproject.toml

# assume directory name is same as package name
PKG_NAME=$(basename $(pwd))

DATA_DIR=.$PKG_NAME-data
LOGFILE=$DATA_DIR/poetry-build.log

mkdir -p $DATA_DIR
date >> $LOGFILE
echo "Making sure pyproject.toml says 'generate-setup-file = true'..." | tee -a $LOGFILE
sed s/'generate-setup-file = false'/'generate-setup-file = true'/g -i pyproject.toml

pip install poetry
POETRY_PATH=$(which poetry)
echo "Found POETRY_PATH=$POETRY_PATH"
echo "$(poetry --version)"

echo "Building package with 'poetry build -f sdist'..." | tee -a $LOGFILE
TARFILE=$(poetry build -f sdist | tee -a $LOGFILE | grep -o -E "$PKG_NAME"'-[vabrc0-9.]+[.]tar[.]gz') 

if [[ -n "$TARFILE" ]]; then
    echo "Built $TARFILE" | tee -a $LOGFILE
    echo "rm -f setup.py" | tee -a $LOGFILE
    echo "tar xvz --file=dist/$TARFILE --wildcards '*/setup.py'" | tee -a $LOGFILE
    rm -f setup.py
    SETUPFILE=$(tar xvz --strip-component=1 --file=dist/$TARFILE --wildcards '*/setup.py' | tee -a $LOGFILE)
    if [[ -f "setup.py" ]]; then 
        echo "Found setup.py so running 'pip install -e .'" | tee -a $LOGFILE
        pip install -e .
        echo "Successfully ran 'pip install -e .'"
    else
        echo "FAILED: Unable to find a setup.py file."
    fi
else
    echo "FAILED: Unable to build setup.py with poetry for installation with pip."
fi
