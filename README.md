Описание

- Сервис читает `.csv` файлы из каталога `input`, прогоняет предобработку и делает предсказания моделью.
- Ранее сервис полагался только на события `watchdog.on_created`, из-за чего файлы, которые были в `input` до старта сервиса, или файлы, создаваемые через bind-mount на Windows, могли быть проигнорированы.
- Внесённые правки: при старте сервис обрабатывает уже существующие файлы; добавлен периодический сканер как fallback; обработанные файлы помечаются во внутреннем наборе `processed_files`.


Запуск (Windows — PowerShell)

1. Перейди в папку `HW`:

```powershell
cd "C:\Users\<пользователь>\...\MTS\MLOps1\HW"
```

2. Собери образ (если ещё не собран):

```powershell
docker build -t fraud-detector .
```

3. Запусти контейнер с примонтированными папками:

```powershell
docker run --rm -it \
  -v "${PWD}\data:/app/data" \
  -v "${PWD}\input:/app/input" \
  -v "${PWD}\output:/app/output" \
  fraud-detector
```

Пояснение: в контейнере путь к входным файлам — `/app/input`, логи пишутся в `/app/logs/service.log` и в stdout.

Запуск (Linux)

1. Перейди в папку `HW`:

```bash
cd /путь/до/MTS/MLOps1/HW
```

2. Собери образ (если ещё не собран):

```bash
docker build -t fraud-detector .
```

3. Для интерактивного запуска (логи в stdout):

```bash
docker run --rm -it \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  fraud-detector
```

4. Для удобного просмотра логов и возможности `exec` запусти контейнер в фоне с именем:

```bash
docker run -d --name fraud-detector \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  fraud-detector
docker logs -f fraud-detector
```

Запуск (macOS)

macOS использует те же команды, что и Linux. Рекомендуется запуск в фоне с именем контейнера для удобства:

```bash
cd /путь/до/MTS/MLOps1/HW
docker build -t fraud-detector .
docker run -d --name fraud-detector \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  fraud-detector
docker logs -f fraud-detector
```

Примечания по macOS и Linux: в отличие от Windows, события файловой системы обычно доставляются более надёжно, но fallback-сканер всё равно полезен для устойчивости.

Проверка обработки файлов (шаги)

1. Оставь контейнер запущенным.
2. В хосте (Windows) в папке `HW\input` сделай одну из операций:
   - Удали существующий CSV и скопируй его обратно под тем же именем.
   - Или скопируй новый файл под другим именем, например `test_2.csv`.
3. В логах контейнера должна появиться строка вида:

```
Processing file: /app/input/test_2.csv
```

Если строка не появилась

- Проверь, что файл виден внутри контейнера:

```powershell
docker exec -it <container_id> ls -la /app/input
```

- Если файл есть внутри контейнера, но `Processing file:` в логах нет — возможна потеря событий от bind-mount на Windows. Периодический сканер (fallback) должен обнаружить файл в течение нескольких секунд и обработать его.

Рекомендации по надёжности

- Для Windows + Docker Desktop рекомендуется использовать комбинацию: `watchdog` для быстрого реагирования и периодический сканер для надёжности.
- Для избежания повторной обработки и для аудита можно:
  - Перемещать обработанные файлы в `input/processed/` после успешной обработки.
  - Либо хранить метаданные обработки (имя файла, timestamp) в SQLite/JSON.

Изменённые файлы

- [HW/app/app.py](app/app.py#L1)

Если хотите — могу:
- Запустить контейнер и мониторить логи прямо сейчас.
- Добавить автоматическое перемещение обработанных файлов в `HW/input/processed/`.
