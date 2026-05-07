# Деплой проекта `acid_claude` на Streamlit Community Cloud

В репозиторий уезжает вся папка `acid_claude/`. Streamlit Cloud запустит файл
`sko_calculator/app.py`. Папки `backend/` и `frontend/` ехать в репо могут, но
Streamlit их не трогает (они для будущего отдельного деплоя FastAPI + Vite).

## 0. Подготовка (один раз)

Внутри `sko_calculator/` уже есть свой `.git` (ранее был отдельный репо). Для
единого репозитория его нужно убрать:

```bash
cd C:\Users\Administrator\Desktop\acid_claude
# удалить вложенный git (он никуда не пушился, просто инит был)
rm -rf sko_calculator/.git
```

> Если боишься — переименуй: `mv sko_calculator/.git sko_calculator/.git.bak`.

## 1. GitHub-репозиторий

```bash
cd C:\Users\Administrator\Desktop\acid_claude
git init
git add .
git status                       # проверь что node_modules / __pycache__ исключены
git commit -m "initial: streamlit sko app"
```

Создай пустой публичный репо на https://github.com/new (например
`acid-claude` или `stimcore-sko`), затем:

```bash
git remote add origin https://github.com/<твой-логин>/<имя-репо>.git
git branch -M main
git push -u origin main
```

## 2. Деплой на Streamlit Cloud

1. https://share.streamlit.io → войди через GitHub.
2. **Create app → Deploy a public app from GitHub**.
3. Параметры:
   - **Repository:** `<твой-логин>/<имя-репо>`
   - **Branch:** `main`
   - **Main file path:** `sko_calculator/app.py`   ← важно, путь относительно корня
   - **App URL:** свой sub-domain, напр. `stimcore-sko`
4. **Deploy**. Сборка ~2 минуты.

Получишь URL `https://<твой-subdomain>.streamlit.app`.

## 3. Что используется при деплое

Streamlit Cloud ищет файлы в корне репо:

| Файл                       | Назначение                                  |
|----------------------------|---------------------------------------------|
| `requirements.txt`         | Python-зависимости приложения               |
| `runtime.txt`              | `python-3.11`                               |
| `.streamlit/config.toml`   | Тема и настройки сервера                    |
| `.gitignore`               | Исключает node_modules, __pycache__, кеши   |

Файлы `sko_calculator/requirements.txt`, `sko_calculator/.streamlit/...`,
`sko_calculator/runtime.txt` остаются для локального запуска внутри подпапки —
не мешают и не дублируют (Cloud берёт из корня).

## 4. Локальный запуск (как и раньше)

```bash
cd C:\Users\Administrator\Desktop\acid_claude\sko_calculator
streamlit run app.py
```

Или из корня:

```bash
cd C:\Users\Administrator\Desktop\acid_claude
streamlit run sko_calculator/app.py
```

## 5. Обновления

`git push` → Cloud сам пересобирает (~30 сек).

## 6. Лимиты бесплатного тарифа

- 1 ГБ RAM
- засыпает после ~7 дней простоя (просыпается за ~30 сек)
- неограничено публичных приложений, 1 приватное

## 7. Если сборка падает

- Логи в правом нижнем углу приложения (**Manage app → Logs**).
- Чаще всего: пакет несовместим с Python 3.11 — закрепи версию в
  `requirements.txt` (`numpy==1.26.4`, `pandas==2.2.2` и т.п.).
- Импорт-ошибка `ModuleNotFoundError: modules` — Streamlit запускает скрипт
  из `sko_calculator/`, относительные импорты `from modules.xxx` работают.

## 8. Бекенд / фронтенд

`backend/` (FastAPI) и `frontend/` (Vite) Streamlit Cloud не запускает. Если
позже захочешь — деплой их отдельно: backend на Render/Railway, frontend на
Vercel/Netlify, и общайся между ними через REST/WebSocket.
