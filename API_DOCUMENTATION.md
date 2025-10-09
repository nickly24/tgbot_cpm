# API Документация для Telegram Bot Admin Panel v2.0

## Обзор

REST API для управления Telegram ботом и чатами с клиентами. Поддерживает статусы клиентов, отслеживание непрочитанных сообщений и полную историю переписки.

**Базовый URL:** `http://0.0.0.0:80/api`  
**Версия:** 2.0.0  
**Дата обновления:** 09.10.2025

## 🔑 Аутентификация

В текущей версии API не требует аутентификации. Все endpoints доступны публично.

⚠️ **Для production рекомендуется добавить JWT или API ключи!**

## 📋 Общие принципы

### Формат ответов

Все ответы возвращаются в формате JSON:

```json
{
  "success": true|false,
  "data": {...},              // при успехе
  "error": "описание ошибки", // при ошибке
  "message": "описание"       // дополнительная информация
}
```

### HTTP коды статусов

- `200` - Успешно
- `400` - Неверный запрос (отсутствуют обязательные поля)
- `404` - Ресурс не найден
- `500` - Внутренняя ошибка сервера

## 📡 API Endpoints

---

## 1️⃣ ЧАТЫ

### GET `/api/chats`

Получить список всех чатов с информацией о пользователях и непрочитанных сообщениях.

**Параметры:** Нет

**Ответ:**

```json
{
  "success": true,
  "data": [
    {
      "chat_id": 123456789,
      "user_info": {
        "user_id": 123456789,
        "username": "username",
        "name": "Иван Петров",
        "created_at": "2025-10-09T12:00:00.000000"
      },
      "status": "student",
      "last_message": {
        "text": "Привет!",
        "timestamp": "2025-10-09T12:30:00.000000",
        "from_user": true
      },
      "unread_count": 5,
      "updated_at": "2025-10-09T12:30:00.000000"
    }
  ]
}
```

**Поля ответа:**

- `chat_id` - ID чата (integer)
- `user_info` - информация о пользователе
- `status` - статус клиента (student, applicant, parent_student, parent_applicant)
- `last_message` - последнее сообщение
- `unread_count` - количество непрочитанных сообщений от клиента
- `updated_at` - время последнего обновления

---

### GET `/api/chats/<chat_id>`

Получить полную историю сообщений чата.

**Параметры:**

- `chat_id` - ID чата (integer, обязательный)

**Пример:** `GET /api/chats/123456789`

**Ответ:**

```json
{
  "success": true,
  "data": {
    "chat_id": 123456789,
    "user_info": {
      "user_id": 123456789,
      "username": "username",
      "name": "Иван Петров",
      "created_at": "2025-10-09T12:00:00.000000"
    },
    "status": "student",
    "status_name": "Студент",
    "messages": [
      {
        "_id": "67068f4a1234567890abcdef",
        "chat_id": 123456789,
        "text": "Привет!",
        "timestamp": "2025-10-09T12:05:00.000000",
        "from_user": true,
        "is_read": false,
        "message_id": 42
      },
      {
        "_id": "67068f4a1234567890abcdeg",
        "chat_id": 123456789,
        "text": "Здравствуйте! Чем могу помочь?",
        "timestamp": "2025-10-09T12:10:00.000000",
        "from_user": false,
        "is_read": true,
        "admin_name": "Менеджер"
      }
    ],
    "unread_count": 1
  }
}
```

**Поля сообщений:**

- `_id` - уникальный ID в MongoDB
- `chat_id` - ID чата
- `text` - текст сообщения
- `timestamp` - время отправки (ISO 8601)
- `from_user` - true = от клиента, false = от админа
- `is_read` - статус прочитанности (актуально только для from_user=true)
- `message_id` - ID сообщения в Telegram (только для сообщений клиента)
- `admin_name` - имя администратора (только для сообщений админа)

---

### POST `/api/chats/<chat_id>/send`

Отправить сообщение клиенту от имени администратора.

**Параметры:**

- `chat_id` - ID чата (integer, обязательный)

**Тело запроса:**

```json
{
  "message": "Текст сообщения",
  "admin_name": "Имя администратора"
}
```

**Обязательные поля:**

- `message` - текст сообщения (string, не пустой)

**Опциональные поля:**

- `admin_name` - имя администратора (string, по умолчанию "Администратор")

**Пример запроса:**

```bash
curl -X POST http://0.0.0.0:80/api/chats/123456789/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Здравствуйте! Чем могу помочь?",
    "admin_name": "Менеджер поддержки"
  }'
```

**Ответ:**

```json
{
  "success": true,
  "message": "Сообщение отправлено успешно"
}
```

**Возможные ошибки:**

- `400` - отсутствует поле "message" или оно пустое
- `500` - не удалось отправить (пользователь заблокировал бота, неверный chat_id)

---

### POST `/api/chats/<chat_id>/mark-read`

Пометить все непрочитанные сообщения от клиента как прочитанные.

**Параметры:**

- `chat_id` - ID чата (integer, обязательный)

**Тело запроса:** Не требуется

**Пример запроса:**

```bash
curl -X POST http://0.0.0.0:80/api/chats/123456789/mark-read
```

**Ответ:**

```json
{
  "success": true,
  "message": "Помечено как прочитано: 5 сообщений",
  "marked_count": 5
}
```

**Поля ответа:**

- `marked_count` - количество помеченных сообщений

⚠️ **Важно:** Вызывайте этот endpoint когда администратор открывает чат!

---

## 2️⃣ ПОЛЬЗОВАТЕЛИ

### GET `/api/chats/<chat_id>/user`

Получить полную информацию о пользователе.

**Параметры:**

- `chat_id` - ID чата (integer, обязательный)

**Ответ:**

```json
{
  "success": true,
  "data": {
    "_id": "67068f4a1234567890abcdef",
    "chat_id": 123456789,
    "user_id": 123456789,
    "username": "username",
    "first_name": "Иван",
    "last_name": "Петров",
    "name": "Иван Петров",
    "status": "student",
    "status_name": "Студент",
    "created_at": "2025-10-09T12:00:00.000000",
    "updated_at": "2025-10-09T12:30:00.000000"
  }
}
```

**Возможные ошибки:**

- `404` - пользователь не найден

---

### PUT `/api/chats/<chat_id>/name`

Обновить имя пользователя (для внутренних нужд админки).

**Параметры:**

- `chat_id` - ID чата (integer, обязательный)

**Тело запроса:**

```json
{
  "name": "Новое имя пользователя"
}
```

**Обязательные поля:**

- `name` - новое имя (string, не пустое)

**Пример запроса:**

```bash
curl -X PUT http://0.0.0.0:80/api/chats/123456789/name \
  -H "Content-Type: application/json" \
  -d '{"name": "Иван Петров (VIP)"}'
```

**Ответ:**

```json
{
  "success": true,
  "message": "Имя пользователя обновлено успешно"
}
```

**Возможные ошибки:**

- `400` - отсутствует поле "name" или оно пустое
- `500` - не удалось обновить

---

## 3️⃣ СТАТУСЫ КЛИЕНТОВ

### GET `/api/statuses`

Получить список всех доступных статусов клиентов.

**Параметры:** Нет

**Ответ:**

```json
{
  "success": true,
  "data": [
    {
      "value": "student",
      "label": "Студент"
    },
    {
      "value": "applicant",
      "label": "Абитуриент"
    },
    {
      "value": "parent_student",
      "label": "Родитель студента"
    },
    {
      "value": "parent_applicant",
      "label": "Родитель абитуриента"
    }
  ]
}
```

---

### GET `/api/chats/<chat_id>/status`

Получить текущий статус клиента.

**Параметры:**

- `chat_id` - ID чата (integer, обязательный)

**Ответ:**

```json
{
  "success": true,
  "data": {
    "chat_id": 123456789,
    "status": "student",
    "status_name": "Студент"
  }
}
```

**Возможные ошибки:**

- `404` - пользователь не найден

---

### PUT `/api/chats/<chat_id>/status`

Обновить статус клиента.

**Параметры:**

- `chat_id` - ID чата (integer, обязательный)

**Тело запроса:**

```json
{
  "status": "applicant"
}
```

**Обязательные поля:**

- `status` - новый статус (string, один из: student, applicant, parent_student, parent_applicant)

**Пример запроса:**

```bash
curl -X PUT http://0.0.0.0:80/api/chats/123456789/status \
  -H "Content-Type: application/json" \
  -d '{"status": "applicant"}'
```

**Ответ:**

```json
{
  "success": true,
  "message": "Статус пользователя обновлен успешно",
  "status_name": "Абитуриент"
}
```

**Возможные ошибки:**

- `400` - отсутствует поле "status", пустое или недопустимое значение
- `500` - не удалось обновить

---

## 4️⃣ СТАТИСТИКА

### GET `/api/stats`

Получить общую статистику по всем чатам.

**Параметры:** Нет

**Ответ:**

```json
{
  "success": true,
  "data": {
    "total_chats": 42,
    "total_unread_messages": 15,
    "status_distribution": {
      "student": 20,
      "applicant": 12,
      "parent_student": 7,
      "parent_applicant": 3
    }
  }
}
```

**Поля ответа:**

- `total_chats` - общее количество чатов
- `total_unread_messages` - общее количество непрочитанных сообщений
- `status_distribution` - распределение по статусам

---

## 5️⃣ СЛУЖЕБНЫЕ

### GET `/api/health`

Проверка работоспособности API.

**Параметры:** Нет

**Ответ:**

```json
{
  "success": true,
  "message": "API работает",
  "timestamp": "2025-10-09T12:00:00.000000"
}
```

---

## 💡 Примеры использования в JavaScript

### Базовый API клиент

```javascript
class TelegramBotAPI {
  constructor(baseURL = "http://0.0.0.0:80/api") {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "API Error");
    }

    return data;
  }

  // Получить все чаты
  async getChats() {
    return this.request("/chats");
  }

  // Получить историю чата
  async getChatHistory(chatId) {
    return this.request(`/chats/${chatId}`);
  }

  // Отправить сообщение
  async sendMessage(chatId, message, adminName = "Администратор") {
    return this.request(`/chats/${chatId}/send`, {
      method: "POST",
      body: JSON.stringify({ message, admin_name: adminName }),
    });
  }

  // Пометить как прочитанное
  async markAsRead(chatId) {
    return this.request(`/chats/${chatId}/mark-read`, {
      method: "POST",
    });
  }

  // Обновить статус
  async updateStatus(chatId, status) {
    return this.request(`/chats/${chatId}/status`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    });
  }

  // Получить статистику
  async getStats() {
    return this.request("/stats");
  }

  // Получить все статусы
  async getStatuses() {
    return this.request("/statuses");
  }
}

// Использование
const api = new TelegramBotAPI();

// Получить чаты
const chats = await api.getChats();
console.log("Чаты:", chats.data);

// Отправить сообщение
await api.sendMessage(123456789, "Привет!", "Менеджер");

// Пометить как прочитанное
await api.markAsRead(123456789);
```

---

## 📝 TypeScript типы

```typescript
// Статусы клиентов
type ClientStatus =
  | "student"
  | "applicant"
  | "parent_student"
  | "parent_applicant";

// Пользователь
interface User {
  chat_id: number;
  user_id: number;
  username: string;
  first_name: string;
  last_name: string;
  name: string;
  status: ClientStatus | null;
  created_at: string;
  updated_at: string;
}

// Сообщение
interface Message {
  _id: string;
  chat_id: number;
  text: string;
  timestamp: string;
  from_user: boolean;
  is_read: boolean;
  message_id?: number;
  admin_name?: string;
}

// Чат
interface Chat {
  chat_id: number;
  user_info: {
    user_id: number;
    username: string;
    name: string;
    created_at: string;
  };
  status: ClientStatus | null;
  last_message: {
    text: string;
    timestamp: string;
    from_user: boolean;
  } | null;
  unread_count: number;
  updated_at: string;
}

// Ответ API
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Статус
interface StatusOption {
  value: ClientStatus;
  label: string;
}

// Статистика
interface Statistics {
  total_chats: number;
  total_unread_messages: number;
  status_distribution: Record<ClientStatus, number>;
}
```

---

## 🎯 Рекомендации для фронтенда

### 1. Автообновление данных

Используйте polling для автоматического обновления:

```javascript
// Обновлять список чатов каждые 5 секунд
setInterval(async () => {
  const chats = await api.getChats();
  updateChatList(chats.data);
}, 5000);

// Обновлять историю активного чата каждые 2 секунды
setInterval(async () => {
  if (activeChatId) {
    const history = await api.getChatHistory(activeChatId);
    updateMessages(history.data.messages);
  }
}, 2000);
```

### 2. Отображение непрочитанных

```javascript
// Показать бейдж с количеством непрочитанных
function ChatBadge({ unreadCount }) {
  if (unreadCount === 0) return null;

  return <span className="badge badge-danger">{unreadCount}</span>;
}
```

### 3. Автоматическая отметка прочитанности

```javascript
// При открытии чата автоматически помечать как прочитанное
async function openChat(chatId) {
  const history = await api.getChatHistory(chatId);

  if (history.data.unread_count > 0) {
    await api.markAsRead(chatId);
    // Обновить список чатов
    refreshChatList();
  }

  displayChat(history.data);
}
```

### 4. Фильтрация по статусам

```javascript
// Фильтр чатов по статусу
function filterChatsByStatus(chats, status) {
  if (status === "all") return chats;
  return chats.filter((chat) => chat.status === status);
}

// Использование
const studentChats = filterChatsByStatus(allChats, "student");
```

---

## 🚨 Обработка ошибок

### Типичные ошибки и решения

| Ошибка                         | Причина                        | Решение                             |
| ------------------------------ | ------------------------------ | ----------------------------------- |
| `404` - Пользователь не найден | Неверный chat_id               | Проверьте ID чата                   |
| `400` - Поле обязательно       | Отсутствует поле в запросе     | Добавьте обязательное поле          |
| `400` - Недопустимый статус    | Неверное значение status       | Используйте только валидные статусы |
| `500` - Не удалось отправить   | Бот заблокирован пользователем | Уведомите администратора            |
| Сетевая ошибка                 | API недоступен                 | Проверьте, запущен ли сервер        |

### Пример обработки

```javascript
try {
  await api.sendMessage(chatId, message);
  showSuccess("Сообщение отправлено");
} catch (error) {
  if (error.message.includes("заблокировал")) {
    showError("Пользователь заблокировал бота");
  } else {
    showError("Ошибка отправки: " + error.message);
  }
}
```

---

## 📚 Дополнительные ресурсы

- **[README.md](README.md)** - Общая документация проекта
- **[REACT_EXAMPLES.md](REACT_EXAMPLES.md)** - Готовые React компоненты
- **[api_examples.json](api_examples.json)** - Примеры JSON ответов

---

**Версия API:** 2.0.0  
**Последнее обновление:** 09.10.2025  
**Поддержка:** Внутренний проект
