#!/bin/sh

# default value for PYTHONBIN=/usr/local/bin/python
# but it change because of poetry that it uses a virtualenv installed within the LAMBDA_TASK_ROOT=/var/task

echo "python installation path and version:"
which python
python --version

echo "lambda-entrypoint.sh: PYTHONPATH ${PYTHONPATH} ..."
echo "lambda-entrypoint.sh: PATH ${PATH} ..."

if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
  exec /usr/local/bin/aws-lambda-rie python -m awslambdaric "$@"
else
  exec python -m awslambdaric "$@"
fi
