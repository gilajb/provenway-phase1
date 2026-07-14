#!/usr/bin/env bash
set -o errexit

pip install -r requirements/production.txt
python manage.py collectstatic --no-input
python manage.py migrate

from django.contrib.auth import get_user_model
U = get_user_model()
u = U.objects.get(email='cjoybett@gmail.com')
u.set_password(os.environ['TEMP_ADMIN_RESET'])
u.save()
print('Password reset done')