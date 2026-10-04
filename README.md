# Drowsy preprocessing

Исследовательский модуль **предобработки и извлечения видео-признаков**, а не
классификатор сонливости. Он читает timestamps и 68-точечные annotations-auto
DROZY, вычисляет геометрические прокси EAR/MAR, причинно выделяет события и
агрегирует шесть групп выходов. Исходные записи не изменяются.

## Установка и запуск

```bash
python -m venv .venv
.venv/bin/pip install -e '.[test]'
drowsy-preprocessing inspect-dataset --config configs/defaults.json --manifest /path/manifest.csv
drowsy-preprocessing extract --config configs/defaults.json --manifest /path/manifest.csv --output runs/example
drowsy-preprocessing evaluate                         # no_ground_truth
drowsy-preprocessing evaluate --annotations manual.csv
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
