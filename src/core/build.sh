set -o errexit

pip install -r src/core/requirements.txt

python src/core/manage.py collectstatic --no-input


python src/core/manage.py migrate