python -m app.main  --- Запустить через питончик просто по обычному)

alembic revision --autogenerate -m "add event on review model" --- Сделать миграцию

alembic upgrade head  --- Применить все миграции

pip install -r requirments.txt  --- Установить зависимости из файла


docker-compose up --build  --- Сбилдить и запустить в докере (НЕ В ФОНЕ)

docker-compose build --- Сбилдить

docker-compose up -d --- Запустить В ФОНЕ


docker-compose down  --- Выключить