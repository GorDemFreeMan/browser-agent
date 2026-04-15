# TZ: Browser Agent Microservice
## Версия: 1.0 (15.04.2026)

---

## 🎯 Цель

Создать отдельный микросервис на Railway для браузерной автоматизации. Агент умеет:
- Заходить на сайты
- Анализировать контент (Vision + парсинг)
- Вводить логин/пароль
- Кликать по элементам
- Делать скриншоты
- Заполнять формы

---

## 🏗️ Архитектура

```
OpenClaw (main)  →  HTTP API  →  Browser Agent (Railway)
                                         ↓
                                   FastAPI
                                   + Playwright
                                   + stealth
                                   + Qwen Vision (local)
```

---

## 🔧 Стек технологий

| Компонент | Назначение |
|-----------|-----------|
| **FastAPI** | Web framework (async) |
| **Playwright** | Browser automation (Chrome/Firefox) |
| **playwright-stealth** | Anti-detection patches |
| **Qwen2.5-VL (local)** | Vision для анализа страниц |
| **Docker** | Контейнеризация |
| **Railway** | Deployment platform |

---

## 📡 API Endpoints

### 1. `POST /browse`
Открыть URL и получить контент
```json
{
  "url": "https://example.com",
  "action": "content" | "screenshot" | "click" | "type"
}
```

### 2. `POST /screenshot`
Сделать скриншот страницы
```json
{
  "url": "https://example.com",
  "full_page": true
}
```

### 3. `POST /click`
Кликнуть по элементу (CSS selector или XPath)
```json
{
  "url": "https://example.com",
  "selector": "#button-id"
}
```

### 4. `POST /type`
Ввести текст в поле
```json
{
  "url": "https://example.com",
  "selector": "#input-id",
  "text": "hello world"
}
```

### 5. `POST /analyze`
Анализ страницы через Vision (Qwen2.5-VL)
```json
{
  "image_url": "data:image/png;base64,...",
  "prompt": "Что видно на странице?"
}
```

### 6. `POST /login`
Авторизация на сайте
```json
{
  "url": "https://example.com/login",
  "username_selector": "#username",
  "password_selector": "#password",
  "submit_selector": "button[type=submit]",
  "username": "user",
  "password": "pass"
}
```

---

## 🚀 Deployment

1. Создать Railway проект (Browser Agent)
2. Dockerfile с Python 3.11 + Playwright + Chrome
3. Environment variables для secrets
4. Health check endpoint `/health`

---

## ⚠️ Требования

- **Минимум ошибок:** playwright-stealth для обхода детекта
- **Максимум функционала:** все 5 операций
- **Бесплатность:** open-source stack
- **Стабильность:** retry logic, timeout handling

---

## 📁 Структура проекта

```
browser-agent/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI entry
│   ├── browser.py       # Playwright wrapper
│   ├── stealth.py       # Stealth patches
│   ├── vision.py        # Qwen integration
│   └── routes/
│       ├── browse.py
│       ├── screenshot.py
│       └── analyze.py
├── Dockerfile
├── requirements.txt
├── railway.json
└── README.md
```

---

## ✅ Definition of Done

1. ✅ Service запускается на Railway
2. ✅ `/browse` возвращает контент страницы
3. ✅ `/screenshot` возвращает PNG
4. ✅ `/click` кликает по элементу
5. ✅ `/type` вводит текст
6. ✅ `/analyze` анализирует через Vision
7. ✅ `/login` авторизуется на сайте
8. ✅ Health check работает
9. ✅ Stealth mode включен

---

## 🔄 Status

| Этап | Status |
|------|--------|
| Research | ✅ Завершён |
| ТЗ | ✅ Создано |
| Code | 🚧 В процессе |
| Test | ⬜ |
| Deploy | ⬜ |

---

*Owner: Максим*
*Created: 15.04.2026*