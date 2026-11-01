# Тесты Part 3

## Описание тестов

### Базовые функции
- **test_normalize_product_name** — нормализация имён товаров (приведение к нижнему регистру, удаление лишних пробелов)
- **test_constants** — проверка значений констант (промпт и заголовки таблицы)

### Представление данных
- **test_get_storage_str_representation** — форматирование хранилища в таблицу (проверка выравнивания, разделители, инварианты)

### CRUD операции
- **test_create_product** — создание товара: валидация имён, проверка дубликатов, генерация ID
- **test_update_product** — обновление товара: валидация, проверка конфликтов имён, обработка отсутствующих ID

### Команды
- **test_run_command_help_exit** — команды help и exit
- **test_run_command_create** — команда create (нормализация имени, округление цены)
- **test_run_command_show** — команда show (вывод таблицы)
- **test_run_command_read** — команда read (чтение товара по ID)
- **test_run_command_update** — команда update (обновление товара)
- **test_run_command_delete** — команда delete (удаление товара)
- **test_run_command_not_a_command** — обработка неверных команд и аргументов
- **test_run_command_invalid_arguments** — парсинг некорректных значений (ID, цена, количество)

### Интеграционные тесты
- **test_show_help** — вывод справки
- **test_print_result** — форматирование результатов команд
- **test_main_session** — полный сеанс работы администратора
- **test_main_catches_invalid_arguments** — обработка ошибок парсинга в main

## Запуск

### Windows
```cmd
# Из корня проекта
python -m pytest src/part3/tests/test_general.py -v

# Или конкретный тест
python -m pytest src/part3/tests/test_general.py::test_normalize_product_name -v
```

### macOS / Linux (Ubuntu, Fedora)
```bash
# Из корня проекта
python -m pytest src/part3/tests/test_general.py -v

# Или конкретный тест
python -m pytest src/part3/tests/test_general.py::test_normalize_product_name -v

# С покрытием кода
python -m pytest src/part3/tests/test_general.py --cov=src/part3 --cov-report=term-missing
```

### Без запуска всех
```bash
# Только быстрые тесты
python -m pytest src/part3/tests/test_general.py -v -k "not main"

# Прерваться на первой ошибке
python -m pytest src/part3/tests/test_general.py -x
```
