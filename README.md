# acid_claude — расчёт солянокислотной обработки (СКО)

Веб-приложение для проектирования солянокислотной обработки нефтегазовых скважин по методике Приложения В (ветка СКО, без HF/ГКО). Дипломный проект.

## Состав репозитория

| Каталог          | Что это                                                      |
|------------------|--------------------------------------------------------------|
| `sko_calculator/`| Streamlit-приложение (основной деплой). Задачи В.1–В.11, В.17 |
| `backend/`       | FastAPI-бэкенд (заготовка под отдельный деплой)              |
| `frontend/`      | Vite + React фронтенд (заготовка под отдельный деплой)       |
| `acid_zone.py`, `plot_b4_schema.py` | Вспомогательные расчётные / графические скрипты |
| `диплом.pdf`, `ЗАДАЧИ_rotated.pdf`  | Методические материалы                            |

## Быстрый запуск (Streamlit)

```bash
pip install -r requirements.txt
streamlit run sko_calculator/app.py
```

Откроется на http://localhost:8501.

## Тесты

```bash
pytest sko_calculator/tests/
```

## Деплой

Streamlit Community Cloud — см. [DEPLOY.md](DEPLOY.md). Точка входа: `sko_calculator/app.py`.

## Подробнее

- Структура задач, поток данных и профиль месторождения: [sko_calculator/README.md](sko_calculator/README.md)
- Инструкция по развёртыванию: [DEPLOY.md](DEPLOY.md)

## Лицензия

См. [LICENSE](LICENSE). Учебно-исследовательский проект.
