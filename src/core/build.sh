set -o errexit

pip install -r src/core/requirements.txt

python manage.py collectstatic --no-input


python manage.py migrate