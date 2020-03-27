## Development setup

```
docker run --name microtools-mongo -d -p 27017:27017 mongo
python manage.py migrate
python manage.py runserver
```

Based on djongo docs, we don't need to `makemigrations` anymore. https://nesdis.github.io/djongo/get-started/
