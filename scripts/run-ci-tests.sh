#/bin/sh

set -ex

# Sanity check: we must be in the root folder of the aiokubernetes repository.
PACKAGE=$( python setup.py --name )
if [ $PACKAGE != "aiokubernetes" ]; then
    echo "This does not look like the aiokubernetes root - abort"
    exit 1
fi

# Ensure no stale files are in the source folder.
find -iname '__pycache__' -type d -exec rm -rf {} \; | true

# Install Make because Sphinx will need it.
apk update && apk add make

# Install the Python requirements.
pip install -r requirements.txt
pip install -r test-requirements.txt

# Style checks.
isort -c
flake8

# Unit tests.
pytest -x -n4

# Build Sphinx documentation.
cd docs
make clean
make html
