# Skills: как подключать навыки в проекты

В `idea_base_seed` навыки живут в `skills/packs/`.

Проект подключает навык через `skills.lock.yaml`:

- `repo`: URL репозитория с навыками (обычно `idea_base_seed`)
- `ref`: tag/commit/branch (рекомендуется tag или commit)
- `path`: путь до пакета внутри репозитория (например `skills/packs/project_analyzer`)
- `install.target`: куда копировать в проект (`tools/skills/<id>`)

## Минимальная схема lock (пример)
```yaml
skills:
  - id: project_analyzer
    source:
      repo: https://github.com/SerjShepelevich/idea_base_seed.git
      ref: main
      path: skills/packs/project_analyzer
    install:
      mode: copy
      target: tools/skills/project_analyzer
```

## Применение
1) `pip install pyyaml`
2) `python3 skillctl.py apply --project . --lock skills.lock.yaml`
3) Запуск entrypoint навыка — вручную (см. README каждого skillpack).
