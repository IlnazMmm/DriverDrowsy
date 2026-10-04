# Отчёт эксперимента

Дата: 2026-10-04. В репозитории не обнаружены DROZY video/landmarks, веса модели
или ручная событийная разметка. Поэтому DROZY smoke, overlay review, IR/RGB,
accuracy и hardware throughput **не выполнялись**, численные результаты не
приводятся. Synthetic suite покрывает 15 и 30 FPS отдельными параметризациями,
нерегулярный шаг, gaps, missing и контракт.

Для закрытия этапа нужны: локальный read-only DROZY с подтверждённой семантикой
interpIndices; видео для ручной overlay-проверки; веса совместимого detector;
независимая разметка blink/closure/gaze/yawn с annotator IDs; subject-disjoint
train/test и временно непересекающиеся окна. Отдельный реальный запуск 15 FPS
должен быть сохранён самостоятельным run artifact.
