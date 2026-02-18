# Skills — как пользоваться библиотекой навыков

Эта инструкция живёт **в репозитории**, чтобы не “растворяться туманом”.
Если нужно подключить навык или добавить новый — открываете этот файл и делаете по шагам.

---

## 1) Модель: suggest → pin → use

- **suggest** — нашли/придумали навык
- **pin** — зафиксировали версию в проекте (`skills.lock.yaml`)
- **use** — применили (установили) и запустили **явно**, без магии

Почему так:
- поиск навыков разрешён и полезен
- но воспроизводимость важнее: проект должен “помнить” точную версию

---

## 2) Где лежат навыки в этом репозитории

- Реестр: `skills/packs/<skill_id>/`
- Шаблон lock: `skills/templates/skills.lock.yaml`
- Менеджер: `skills/skillctl.py` (git → copy, без авто‑запуска)

---

## 3) Подключить навык в любой проект

### 3.1 Создать `skills.lock.yaml` в проекте

Рекомендуется **tag или commit**, не `main`.

```yaml
skills:
  - id: project_analyzer
    source:
      repo: https://github.com/SerjShepelevich/idea_base_seed.git
      ref: skills-v0.1.0      # tag или commit
      path: skills/packs/project_analyzer
    install:
      mode: copy
      target: tools/skills/project_analyzer
```

### 3.2 Применить lock (установить skillpack)

Требования:
- `git` установлен
- `pip install pyyaml`

Команда (из корня проекта):
```bash
pip install pyyaml
python3 /ABS/PATH/TO/idea_base_seed/skills/skillctl.py apply --project . --lock skills.lock.yaml
```

Что будет:
- файлы навыка появятся в `tools/skills/<id>/`
- создастся кэш `.skills_cache/` в проекте (его обычно добавляют в `.gitignore`)

---

## 4) Запуск первого навыка: `project_analyzer` (MVP)

Запуск из корня проекта:
```bash
python3 tools/skills/project_analyzer/src/project_analyzer.py --root . --out plan/project_architecture.json
```

Контракт:
- выходной файл: `plan/project_architecture.json`

Smoke-test:
```bash
python3 -m unittest tools/skills/project_analyzer/tests/test_project_analyzer.py
```

---

## 5) Обновить навык в проекте

1) В проекте меняете `ref:` в `skills.lock.yaml` на новый tag/commit  
2) Повторяете apply:
```bash
python3 /ABS/PATH/TO/idea_base_seed/skills/skillctl.py apply --project . --lock skills.lock.yaml
```

---

## 6) Добавить новый навык (skill-pack) в `idea_base_seed`

### 6.1 Шаблон структуры
```
skills/packs/<skill_id>/
  skill.yaml
  README.md
  src/
  tests/
```

### 6.2 Минимальный чек-лист качества

Навык считается не-черновиком, если:
- есть `skill.yaml` с `id/version/status/entrypoints/contracts`
- есть `README.md` (как запускать)
- есть `tests/` (хотя бы smoke)
- есть tag `skills-vX.Y.Z` после изменения (чтобы проекты могли pin)

---

## 7) Типовые проблемы

**A) PyYAML не найден**
```bash
pip install pyyaml
```

**B) `pack not found`**
Проверьте `repo/ref/path` в lock. Самая частая ошибка — неверный `path`.

**C) “не обновилось”**
Если `ref` указывает на `main`, вы ловите дрейф. Используйте tag/commit.

---

## 8) Рекомендованная политика версий

После мержа набора навыков:
```bash
git tag skills-v0.1.0
git push --tags
```

И в проектах:
- `ref: skills-v0.1.0`
- дальше обновлять осознанно (меняя `ref`)
