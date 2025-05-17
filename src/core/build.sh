set -o errexit

pip install -r src/core/requirements.txt

py manage.py collectstatic --no-input


py manage.py migrate