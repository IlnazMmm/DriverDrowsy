# Setup

Цель — CPython 3.11+. Минимумы зависимостей зафиксированы в `pyproject.toml`;
конкретное воспроизводимое окружение сохраняйте командой
`python -m pip freeze > runs/<id>/environment.lock.txt`. Пакет не скачивает
датасеты и веса. OpenCV нужен только для чтения видео/overlay; DROZY landmarks
baseline не требует модели.

Для live/video detection необходимо передать реализацию `LandmarkBackend` с
локально доступными и хешированными весами. Встроенный unavailable backend
завершается диагностической ошибкой и не является рабочим detector.

## Windows: команда не распознана

Console script появляется только после успешного `pip install`. В PowerShell
рекомендуется не полагаться на активацию окружения или `PATH`, а явно использовать
его Python:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m drowsy_preprocessing --help
```

Эквивалентный launcher находится по адресу
`.\.venv\Scripts\drowsy-preprocessing.exe`. Если `pip install` завершился
ошибкой, сначала следует исправить именно эту ошибку: наличие checkout исходного
кода само по себе не добавляет команду в систему.
