# Drowsy preprocessing

Исследовательский модуль **предобработки и извлечения видео-признаков**, а не
классификатор сонливости. Он читает timestamps и 68-точечные annotations-auto
DROZY, вычисляет геометрические прокси EAR/MAR, причинно выделяет события и
агрегирует шесть групп выходов. Исходные записи не изменяются.

## Установка и запуск

Команда `drowsy-preprocessing` создаётся **при установке пакета** и находится в
каталоге `Scripts` виртуального окружения. Надёжнее запускать тот же CLI через
Python виртуального окружения: такой вариант не зависит от `PATH`.

### Windows PowerShell

Из корня репозитория:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m drowsy_preprocessing --help
.\.venv\Scripts\python.exe -m drowsy_preprocessing inspect-dataset --config configs/defaults.json --manifest C:\path\to\manifest.csv
```

После установки можно также вызывать созданный launcher напрямую, не активируя
окружение:

```powershell
.\.venv\Scripts\drowsy-preprocessing.exe --help
```

Если PowerShell сообщает, что имя `drowsy-preprocessing` не распознано, это
означает, что пакет не установлен в текущий Python либо каталог `.venv\Scripts`
не находится в `PATH`. Используйте приведённую выше команду
`.\.venv\Scripts\python.exe -m drowsy_preprocessing ...` и проверьте установку:

```powershell
.\.venv\Scripts\python.exe -m pip show drowsy-preprocessing
```

Не запускайте только `drowsy-preprocessing` до установки пакета.

### Linux/macOS

```bash
python -m venv .venv
.venv/bin/pip install -e '.[test]'
.venv/bin/python -m drowsy_preprocessing inspect-dataset --config configs/defaults.json --manifest /path/manifest.csv
.venv/bin/python -m drowsy_preprocessing extract --config configs/defaults.json --manifest /path/manifest.csv --output runs/example
.venv/bin/python -m drowsy_preprocessing evaluate                         # no_ground_truth
.venv/bin/python -m drowsy_preprocessing evaluate --annotations manual.csv
```

Формат манифеста показан в `templates/manifest.csv`. Относительные пути
разрешаются от каталога манифеста. `interpIndices` намеренно блокирует extraction,
пока его семантика не подтверждена и явно не записана в конфигурации. Длины
timestamps/landmarks обязаны совпадать; тихого усечения нет.

Результат: независимые `frames.jsonl`, `events.jsonl`, `windows.jsonl` и
`run_metadata.json`. Production-окно — 60 s с шагом 1 s; доступны также
исследовательские 30/120 s. Числа в `configs/defaults.json` — стартовые гипотезы,
не универсальные нормы.

## Статус признаков

| Группа | Статус baseline | Примечание |
|---|---|---|
| PERCLOS | measured (геометрический baseline) | Временная доля порогового состояния EAR; EAR не является физической долей закрытия века |
| Частота моргания | measured | Только завершённые события, реальные timestamps |
| Длительность моргания | measured | `null`, если завершённых событий нет |
| Направление взгляда | unavailable | 68 точек без радужки недостаточно; нужен валидированный backend |
| Длительность зевоты | proxy | MAR-событие `yawn_candidate`, не подтверждённый зевок |
| Частота зевоты | proxy | Частота `yawn_candidate` при доступном сигнале рта |

## Границы

Нет весов, видео DROZY и ручной разметки, поэтому не заявляются accuracy,
готовность live backend, пригодность для реального автомобиля или полное
соответствие ПНСТ 1054-2026. KSS не используется как покадровая разметка.
Модуль не реализует CAN, носимые датчики, сонливость, прогноз, нечёткий вывод или
предупреждение. Подробнее: `docs/limitations.md` и `docs/experiments.md`.
