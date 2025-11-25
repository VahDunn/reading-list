# 1. Остановить и удалить контейнеры + volume БД
docker-compose down -v

# 2. Поднять чистые контейнеры
docker-compose up --build -d

# 3. Применить миграции
docker-compose exec api python -m alembic upgrade head

# 4. Прогнать сиды
docker-compose exec api python -m reading_list.db.seed

# 5. Проверка
curl http://localhost:8000/health

sWaG - http://localhost:8000/docs
