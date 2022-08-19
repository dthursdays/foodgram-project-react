# praktikum_new_diplom
Нужно добавить в папку infra/ файл .env:
'''
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
'''
Далее:
'''
cd infra
docker-compose up -d --build
'''

'''
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
docker-compose exec web python manage.py loaddata dump.json 
'''
В dump.json, - ингредиенты и тэги