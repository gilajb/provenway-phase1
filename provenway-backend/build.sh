#!/usr/bin/env bash
set -o errexit

pip install -r requirements/production.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "import os; from django.contrib.auth import get_user_model; U = get_user_model(); u, created = U.objects.get_or_create(email='cjoybett@gmail.com', defaults={'is_staff': True, 'is_superuser': True}); u.is_staff = True; u.is_superuser = True; u.set_password(os.environ['TEMP_ADMIN_RESET']); u.save(); print('Created' if created else 'Updated')"
