# Setup

Цель — CPython 3.11+. Минимумы зависимостей зафиксированы в `pyproject.toml`;
конкретное воспроизводимое окружение сохраняйте командой
`python -m pip freeze > runs/<id>/environment.lock.txt`. Пакет не скачивает
датасеты и веса. OpenCV нужен только для чтения видео/overlay; DROZY landmarks
baseline не требует модели.

Для live/video detection необходимо передать реализацию `LandmarkBackend` с
локально доступными и хешированными весами. Встроенный unavailable backend
завершается диагностической ошибкой и не является рабочим detector.
