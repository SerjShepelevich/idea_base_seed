# Skills (registry inside idea_base_seed)

Эта папка — **единое хранилище навыков** (skill-packs) внутри репозитория `idea_base_seed`.

Принцип: **suggest → pin → use**
- suggest: агент/человек предлагает навык
- pin: проект фиксирует конкретную версию навыка в `skills.lock.yaml`
- use: навык применяется/запускается явно

## Структура
- `skills/packs/<skill_id>/` — содержимое навыка (код/README/tests/skill.yaml)
- `skills/templates/skills.lock.yaml` — шаблон lock-файла для проектов
- `skills/skillctl.py` — минимальный установщик skillpacks (git → copy)

## Как использовать в проекте (быстро)
1) Положите в проект `skills.lock.yaml` (можно взять из `skills/templates/skills.lock.yaml` и поправить `ref:` на tag/commit).
2) Установите зависимость:
   ```bash
   pip install pyyaml
   ```
3) Скопируйте `skills/skillctl.py` в проект (например, `tools/skillctl.py`) или запускайте по абсолютному пути.
4) Примените:
   ```bash
   python3 tools/skillctl.py apply --project . --lock skills.lock.yaml
   ```

## Важно
- `skillctl` **не запускает** навыки автоматически — только копирует файлы.
- Запуск навыка делаете вы (явно), чтобы избежать "магии".
