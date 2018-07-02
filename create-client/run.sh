#!/bin/bash

# Build the latest set of Kubernetes client models with Swagger and copy them into
# the `aiokubernetes` module
#
# This is a convenience script to explicitly document every build step that was
# necessary to create this library. Furthermore, it will (hopefully) make it easy
# to upgrade the generated models when a new Kubernetes version is released.

set -ex

# Convenience.
SCRIPT_ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
OPENAPI_DIR="$SCRIPT_ROOT/gen/openapi"
AIOK8S_DIR="$SCRIPT_ROOT/.."

# Clone the client generator repository unless it exists already.
if [ ! -d gen/ ]; then
    #git clone https://github.com/kubernetes-client/gen.git
    git clone https://github.com/olitheolix/gen.git gen
fi

pushd "$OPENAPI_DIR"

# Check out the specific code generator version that we know will work.
git checkout 202c5faa7500fb250dc9c31237304b4181a6732f

# Use the Swagger generator to build the K8s models.
rm -rf "$OPENAPI_DIR/aiokubernetes"
./python-async-generic.sh aiokubernetes "${SCRIPT_ROOT}/settings"

# Copy the generated files/folder to the correct location of the `aiokubernetes` client library.
cp -r aiokubernetes/test aiokubernetes/docs "$AIOK8S_DIR/"
cp -r aiokubernetes/aiokubernetes/api aiokubernetes/aiokubernetes/models "$AIOK8S_DIR/aiokubernetes/"

# The __init__ file contains just contains convenience imports. These serve as a
# sanity check that all generated models are indeed in our `api/` folder.
cp -r aiokubernetes/aiokubernetes/__init__.py "$AIOK8S_DIR/aiokubernetes/__init__.py"

# Import the main components in __init__ file for convenience library usage.
cat >>"$AIOK8S_DIR/aiokubernetes/__init__.py" <<EOF

# These import are unnecessary but make imports more convenient.
import aiokubernetes.api as api
import aiokubernetes.config as config
import aiokubernetes.models as models
import aiokubernetes.stream as stream
import aiokubernetes.watch as watch
EOF

popd
