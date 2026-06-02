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
