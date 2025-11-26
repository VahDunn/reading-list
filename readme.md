# Reading-list - микросервис - Items, Tags 


Дисклеймер - логгер не настроен, поэтому алхимия пишет в консоль
+ seed внутри, чтобы все работало "из коробки"
+ все сервисы требуют пользователя, но это в dummy формате
+ есть неоднозначные архитектурные решения, но в целом это то, как я себе представляю сервис по солиду
## Запуск - из корня проекта
1. Убрать .example для .env.example, опционально поменять конфиг на желаемый
2. Поднять чистые контейнеры
```docker-compose up ```
3. Применить миграции
```docker-compose exec api python -m alembic upgrade head```
4. Прогнать сиды
```docker-compose exec api python -m reading_list.db.seed```


## Проверка
```
curl http://localhost:8000/health
```
- должен отвечать ok если все работает
http://localhost:8000/docs - Страница с автодоками на Сваггере

X-User-Id в заголовке - id пользователя
Если не передавать, будет 1 (упрощение)
Пользователя в сиде два
```
curl --location --request POST 'http://0.0.0.0:8000/api/v1/items' \
--header 'Content-Type: application/json' \
--data '{
  "title": "Clean Architecture",
  "kind": "book",
  "status": "planned",
  "priority": "high",
  "notes": "Прочитать до конца месяца",
  "tag_ids": [1, 2]
}'
```
Пост-запрос на создание item


```
curl --location 'http://0.0.0.0:8000/api/v1/items'
```

Гет-запрос на получение всех Item (должен включать созданный)


```
curl --location 'http://0.0.0.0:8000/api/v1/tags' \
--header 'Content-Type: application/json' \
--data '{
  "name": "python"
}'
```

POST-запрос на создание тега (специфично для пользователя)


```
curl --location 'http://0.0.0.0:8000/api/v1/tags'
```

Запрос на получение всех тэгов (включая созданный)

Items можно создавать одинаковые, теги уникальны для пользователя

Для пагинации - лучше в Постмане/Браузере

Там же можно выбрать лимит и оффсет

В сидах информации мало,
поэтому, чтобы проверить работоспособность, нужно потыкать POST на Items раз 10-15.


GET
```
http://0.0.0.0:8000/api/v1/items?limit=10&offset=0&sort_by=created_at&sort_dir=desc
```

```
http://0.0.0.0:8000/api/v1/items?status=planned&kind=book&priority=high&tag_ids=1&tag_ids=3&q=clean&created_from=2025-11-01T00:00:00&created_to=2025-11-30T23:59:59&limit=10&offset=0&sort_by=created_at&sort_dir=desc
```


Привязка тега к айтему

```
curl --location 'http://0.0.0.0:8000/api/v1/items' \
--header 'Content-Type: application/json' \
--data '{
  "title": "Clean Architecture",
  "kind": "book"
}
'
```
ответ
```json
{
    "id": 32,
    "user_id": 1,
    "title": "Clean Architecture",
    "kind": "book",
    "status": "planned",
    "priority": "normal",
    "notes": null,
    "created_at": "2025-11-26T13:42:16.111926Z",
    "updated_at": "2025-11-26T13:42:16.111926Z",
    "tag_ids": []
}
```
Это айтем без тегов

Далее PATCH на айтем (по id) с id тегов 
```
curl --location --request PATCH 'http://0.0.0.0:8000/api/v1/items/32' \
--header 'Content-Type: application/json' \
--data '{
  "tag_ids": [1, 2]
}'
```

И ответ
```json
{
    "id": 32,
    "user_id": 1,
    "title": "Clean Architecture",
    "kind": "book",
    "status": "planned",
    "priority": "normal",
    "notes": null,
    "created_at": "2025-11-26T13:42:16.111926Z",
    "updated_at": "2025-11-26T13:42:16.111926Z",
    "tag_ids": [
        1,
        2
    ]
}
```

Для пользователей - POST

```
curl --location 'http://0.0.0.0:8000/api/v1/users/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "hades@example.com",
    "display_name": "Hades"
  }'
```
И ответ

```
    "display_name": "Hades",
    "id": 3,
    "created_at": "2025-11-26T14:26:38.377057Z",
    "email": "hades@example.com"
}
```

Потом GET 

```
curl --location 'http://0.0.0.0:8000/api/v1/users/'
```

Потом DELETE

```
curl --location --request DELETE 'http://0.0.0.0:8000/api/v1/users/3'
```

DELETE на любую сущность возвращает id удаленного объекта (опционально)

Для удаления конкретных тегов


```
curl --location --request DELETE 'http://0.0.0.0:8000/api/v1/items/1/tags' \
--header 'Content-Type: application/json' \
--data '{
  "tag_ids": [2]
}'
```

Возвращается полный объект с обновленным списком тегов

Юнит-тесты

Перед запуском 

```
python -m venv venv
source venv/bin/activate
 pip install .'[dev]'
```

И далее

```
python -m pytest
```

Репо мокнул целиком, через sqlite можно было, но там id требуется как int а не bigint
Можно было бы через постгрес, но локально поднимать в данном случае того не стоит
Тесты базовые, на один сервис