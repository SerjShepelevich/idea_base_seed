# idea_base_seed — база идей и навыков

Этот репозиторий — единое место, где мы храним:
- **Идеи / решения** (docs/)
- **Навыки (skills)** — переносимые “skill-packs”, которые можно подключать к любому проекту через `skills.lock.yaml`

## Куда смотреть
- `docs/IDEAS.md` — список идей (ссылки на карточки)
- `docs/DECISIONS.md` — журнал решений
- `docs/SKILLS.md` — **операционный гайд** по навыкам (как подключать/обновлять/добавлять)
- `skills/packs/` — сами skill-packs
- `skills/skillctl.py` — минимальный менеджер (git → copy, без авто‑выполнения кода)

## Быстрый старт (подключить skill в проект)
1) В проекте создайте `skills.lock.yaml` (см. `docs/SKILLS.md`)
2) Установите зависимость: `pip install pyyaml`
3) Примените lock:  
   `python3 /ABS/PATH/TO/idea_base_seed/skills/skillctl.py apply --project . --lock skills.lock.yaml`
