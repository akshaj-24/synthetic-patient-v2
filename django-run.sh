conda deactivate
cd ~
cd synthetic-patient-v2
source .venv/bin/activate
cd backend
python manage.py migrate
python manage.py runserver 8080