# Деплой на Streamlit Community Cloud

## 1. Подготовка GitHub-репозитория

```bash
cd sko_calculator
git init                       # если репо ещё нет (у тебя уже есть .git)
git add .
git commit -m "prepare for streamlit cloud deploy"
```

Создай новый публичный репозиторий на https://github.com/new (например `sko-calculator`)
и запушь:

```bash
git remote add origin https://github.com/<твой-логин>/sko-calculator.git
git branch -M main
git push -u origin main
```

## 2. Деплой на Streamlit Cloud

1. Открой https://share.streamlit.io и войди через GitHub.
2. Нажми **Create app → Deploy a public app from GitHub**.
3. Заполни форму:
   - **Repository:** `<твой-логин>/sko-calculator`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (optional):** свой sub-domain, например `stimcore-sko`
4. Жми **Deploy** — сборка ~2 минуты.
5. Получишь публичный URL: `https://stimcore-sko.streamlit.app`

## 3. Что в репозитории нужно (всё уже готово)

- `app.py` — главный файл приложения
- `modules/` — модули
- `config.json` — дефолтный профиль (Предкарпатье)
- `requirements.txt` — зависимости (streamlit, numpy, scipy, plotly, pandas, reportlab, python-docx)
- `runtime.txt` — версия Python (3.11)
- `.streamlit/config.toml` — тема
- `.gitignore` — исключает `__pycache__`, `.venv`, секреты

## 4. Обновления

После любого `git push` в `main` Streamlit Cloud автоматически пересобирает и
перезапускает приложение (~30 секунд).

## 5. Лимиты бесплатного тарифа

- 1 ГБ RAM
- засыпает после ~7 дней простоя (просыпается за 30 сек при заходе)
- 1 приватное приложение, неограничено публичных
- ресурсная квота — на разумное использование

## 6. Если нужны секреты

Создай в админке приложения раздел **Settings → Secrets** и добавь TOML:

```toml
[my_section]
api_key = "..."
```

Читай в коде через `st.secrets["my_section"]["api_key"]`. Файл
`.streamlit/secrets.toml` локально уже исключён `.gitignore`.

## 7. Если сборка падает

- Проверь логи в правом нижнем углу приложения (**Manage app**).
- Чаще всего — несовместимость пакета с Python 3.11. Пин нужной версии в
  `requirements.txt` (например `numpy==1.26.4`).
