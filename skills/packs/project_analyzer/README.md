# project_analyzer (MVP)

## Запуск
Из корня проекта:
```bash
python3 tools/skills/project_analyzer/src/project_analyzer.py --root . --out plan/project_architecture.json
```

## Выходной контракт
- `plan/project_architecture.json`
- Детерминированная сортировка (пути/имена)

## Что улучшать дальше
- граф импортов/зависимостей
- сигнатуры функций (args/kwargs), docstring
- плагины под ROS2/Unitree/KUKA/URScript
