# API Документация - Настройки и Конфигурация v2.2

## 📋 Обзор

Новые API endpoints для управления настройками бота:

- **Сообщения бота** - редактирование текстов, которые бот отправляет пользователям
- **Статусы клиентов** - динамическое управление статусами через админку

**Версия:** 2.2.0  
**Дата обновления:** 12.10.2025

---

## 🔧 СООБЩЕНИЯ БОТА

### GET `/api/bot-messages`

Получить все сообщения бота.

**Ответ:**

```json
{
  "success": true,
  "data": {
    "welcome": "Привет! 👋\n\nЯ бот для связи с администратором.\n\nКак мне вас называть? Напишите ваше имя:",
    "ask_status": "Приятно познакомиться, {name}! 😊\n\nТеперь выберите, кто вы:",
    "status_selected": "✅ Отлично! Вы выбрали статус: {status_name}\n\nТеперь можете отправлять мне текстовые сообщения...",
    "welcome_back": "С возвращением, {name}! 👋\n\nВаш статус: {status_name}\n\n...",
    "message_received": "✅ Ваше сообщение получено и передано администратору. Ожидайте ответа!",
    "unsupported_message": "❌ Извините, я обрабатываю только текстовые сообщения...",
    "need_status": "⚠️ Пожалуйста, сначала выберите ваш статус с помощью кнопок выше.",
    "admin_message_prefix": "📩 Сообщение от {admin_name}:\n\n"
  }
}
```

**Плейсхолдеры в сообщениях:**

- `{name}` - имя пользователя
- `{status_name}` - название статуса (человекочитаемое)
- `{admin_name}` - имя администратора

---

### PUT `/api/bot-messages`

Обновить все сообщения бота одним запросом.

**Тело запроса:**

```json
{
  "messages": {
    "welcome": "Новый текст приветствия",
    "ask_status": "Новый текст для выбора статуса",
    ...
  }
}
```

**Ответ:**

```json
{
  "success": true,
  "message": "Сообщения бота обновлены успешно"
}
```

**Возможные ошибки:**

- `400` - Поле 'messages' обязательно или должно быть объектом
- `500` - Не удалось обновить сообщения

---

### GET `/api/bot-messages/<message_key>`

Получить конкретное сообщение бота по ключу.

**Параметры:**

- `message_key` - ключ сообщения (welcome, ask_status, и т.д.)

**Пример:** `GET /api/bot-messages/welcome`

**Ответ:**

```json
{
  "success": true,
  "data": {
    "key": "welcome",
    "text": "Привет! 👋\n\nЯ бот для связи с администратором..."
  }
}
```

**Возможные ошибки:**

- `404` - Сообщение не найдено

---

### PUT `/api/bot-messages/<message_key>`

Обновить конкретное сообщение бота.

**Параметры:**

- `message_key` - ключ сообщения

**Тело запроса:**

```json
{
  "text": "Новый текст сообщения с {плейсхолдерами}"
}
```

**Пример:**

```bash
curl -X PUT http://0.0.0.0:80/api/bot-messages/welcome \
  -H "Content-Type: application/json" \
  -d '{"text": "Добро пожаловать! Как вас зовут?"}'
```

**Ответ:**

```json
{
  "success": true,
  "message": "Сообщение 'welcome' обновлено успешно"
}
```

**Возможные ошибки:**

- `400` - Поле 'text' обязательно или пустое
- `500` - Не удалось обновить сообщение

---

## 👥 УПРАВЛЕНИЕ СТАТУСАМИ

### GET `/api/config/statuses`

Получить все статусы клиентов из конфигурации (с полной информацией).

**Ответ:**

```json
{
  "success": true,
  "data": [
    {
      "value": "student",
      "label": "Студент",
      "emoji": "👨‍🎓",
      "is_system": true,
      "order": 0,
      "created_at": "2025-10-12T10:00:00.000000"
    },
    {
      "value": "reserve",
      "label": "Резерв",
      "emoji": "📝",
      "is_system": true,
      "order": 1,
      "created_at": "2025-10-12T10:00:00.000000"
    },
    {
      "value": "applicant",
      "label": "Абитуриент",
      "emoji": "🎓",
      "is_system": false,
      "order": 2,
      "created_at": "2025-10-12T10:00:00.000000"
    }
  ]
}
```

**Поля статуса:**

- `value` - уникальное значение статуса (используется в коде)
- `label` - отображаемое название
- `emoji` - эмодзи для кнопки
- `is_system` - системный статус (нельзя удалить, ограниченное редактирование)
- `order` - порядок отображения
- `created_at` - дата создания
- `updated_at` - дата обновления (опционально)

**Системные статусы:**

- `student` (Студент) - обязательный, нельзя удалить
- `reserve` (Резерв) - обязательный, нельзя удалить

Для системных статусов можно редактировать только `label` и `emoji`.

---

### POST `/api/config/statuses`

Добавить новый статус клиента.

**Тело запроса:**

```json
{
  "value": "vip_client",
  "label": "VIP Клиент",
  "emoji": "⭐"
}
```

**Обязательные поля:**

- `value` - уникальное значение (только буквы, цифры, подчеркивания)
- `label` - отображаемое название

**Опциональные поля:**

- `emoji` - эмодзи для кнопки (по умолчанию пусто)

**Пример:**

```bash
curl -X POST http://0.0.0.0:80/api/config/statuses \
  -H "Content-Type: application/json" \
  -d '{
    "value": "graduate",
    "label": "Выпускник",
    "emoji": "🎓"
  }'
```

**Ответ:**

```json
{
  "success": true,
  "message": "Статус добавлен успешно",
  "data": {
    "value": "graduate",
    "label": "Выпускник",
    "emoji": "🎓",
    "is_system": false,
    "order": 5,
    "created_at": "2025-10-12T10:30:00.000000"
  }
}
```

**Возможные ошибки:**

- `400` - Поле 'value' или 'label' обязательно
- `400` - Значение и название не могут быть пустыми
- `400` - Значение может содержать только буквы, цифры и подчеркивания
- `400` - Такой статус уже существует

---

### PUT `/api/config/statuses/<status_value>`

Обновить существующий статус.

**Параметры:**

- `status_value` - значение статуса для обновления

**Тело запроса:**

```json
{
  "label": "Новое название",
  "emoji": "🆕",
  "order": 3
}
```

**Для системных статусов:**

- Можно обновить только `label` и `emoji`
- Нельзя изменить `value` и `is_system`

**Для не системных статусов:**

- Можно обновить `label`, `emoji`, `order`, `value`

**Пример:**

```bash
curl -X PUT http://0.0.0.0:80/api/config/statuses/applicant \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Поступающий",
    "emoji": "📚"
  }'
```

**Ответ:**

```json
{
  "success": true,
  "message": "Статус обновлен успешно"
}
```

**Возможные ошибки:**

- `400` - Нет данных для обновления
- `400` - Название не может быть пустым
- `404` - Статус не найден
- `500` - Не удалось обновить статус

---

### DELETE `/api/config/statuses/<status_value>`

Удалить статус клиента (только не системные).

**Параметры:**

- `status_value` - значение статуса для удаления

**Пример:**

```bash
curl -X DELETE http://0.0.0.0:80/api/config/statuses/applicant
```

**Ответ:**

```json
{
  "success": true,
  "message": "Статус удален успешно"
}
```

**Возможные ошибки:**

- `403` - Нельзя удалить системный статус
- `404` - Статус не найден
- `500` - Не удалось удалить статус

⚠️ **ВАЖНО:** Системные статусы (`student`, `reserve`) нельзя удалить!

---

## 📊 СТАРЫЙ ENDPOINT (совместимость)

### GET `/api/statuses`

Получить список всех статусов (совместимость со старым API).

Возвращает упрощенный формат без is_system, order и других полей.

**Ответ:**

```json
{
  "success": true,
  "data": [
    { "value": "student", "label": "Студент" },
    { "value": "reserve", "label": "Резерв" },
    { "value": "applicant", "label": "Абитуриент" }
  ]
}
```

Рекомендуется использовать `/api/config/statuses` для получения полной информации.

---

## 💻 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### JavaScript/Fetch

```javascript
// Получить все сообщения бота
async function getBotMessages() {
  const response = await fetch("http://0.0.0.0:80/api/bot-messages");
  const data = await response.json();
  return data.data;
}

// Обновить сообщение приветствия
async function updateWelcomeMessage(newText) {
  const response = await fetch("http://0.0.0.0:80/api/bot-messages/welcome", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: newText }),
  });
  return await response.json();
}

// Получить все статусы
async function getStatuses() {
  const response = await fetch("http://0.0.0.0:80/api/config/statuses");
  const data = await response.json();
  return data.data;
}

// Добавить новый статус
async function addStatus(value, label, emoji) {
  const response = await fetch("http://0.0.0.0:80/api/config/statuses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value, label, emoji }),
  });
  return await response.json();
}

// Обновить статус
async function updateStatus(value, updates) {
  const response = await fetch(
    `http://0.0.0.0:80/api/config/statuses/${value}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    }
  );
  return await response.json();
}

// Удалить статус
async function deleteStatus(value) {
  const response = await fetch(
    `http://0.0.0.0:80/api/config/statuses/${value}`,
    {
      method: "DELETE",
    }
  );
  return await response.json();
}
```

### React Hook Example

```jsx
import { useState, useEffect } from "react";

function BotMessagesEditor() {
  const [messages, setMessages] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMessages();
  }, []);

  const loadMessages = async () => {
    try {
      const response = await fetch("http://0.0.0.0:80/api/bot-messages");
      const data = await response.json();
      if (data.success) {
        setMessages(data.data);
      }
    } catch (error) {
      console.error("Ошибка загрузки сообщений:", error);
    } finally {
      setLoading(false);
    }
  };

  const updateMessage = async (key, text) => {
    try {
      const response = await fetch(
        `http://0.0.0.0:80/api/bot-messages/${key}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        }
      );

      const data = await response.json();
      if (data.success) {
        alert("Сообщение обновлено!");
        loadMessages();
      }
    } catch (error) {
      console.error("Ошибка обновления:", error);
    }
  };

  if (loading) return <div>Загрузка...</div>;

  return (
    <div>
      <h2>Редактор сообщений бота</h2>
      {Object.entries(messages).map(([key, text]) => (
        <div key={key}>
          <h3>{key}</h3>
          <textarea
            value={text}
            onChange={(e) => {
              setMessages({ ...messages, [key]: e.target.value });
            }}
          />
          <button onClick={() => updateMessage(key, messages[key])}>
            Сохранить
          </button>
        </div>
      ))}
    </div>
  );
}

function StatusesManager() {
  const [statuses, setStatuses] = useState([]);
  const [newStatus, setNewStatus] = useState({
    value: "",
    label: "",
    emoji: "",
  });

  useEffect(() => {
    loadStatuses();
  }, []);

  const loadStatuses = async () => {
    try {
      const response = await fetch("http://0.0.0.0:80/api/config/statuses");
      const data = await response.json();
      if (data.success) {
        setStatuses(data.data);
      }
    } catch (error) {
      console.error("Ошибка загрузки статусов:", error);
    }
  };

  const addStatus = async () => {
    try {
      const response = await fetch("http://0.0.0.0:80/api/config/statuses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newStatus),
      });

      const data = await response.json();
      if (data.success) {
        alert("Статус добавлен!");
        loadStatuses();
        setNewStatus({ value: "", label: "", emoji: "" });
      }
    } catch (error) {
      console.error("Ошибка добавления:", error);
    }
  };

  const deleteStatus = async (value) => {
    if (!confirm("Удалить этот статус?")) return;

    try {
      const response = await fetch(
        `http://0.0.0.0:80/api/config/statuses/${value}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();
      if (data.success) {
        alert("Статус удален!");
        loadStatuses();
      } else {
        alert(data.error);
      }
    } catch (error) {
      console.error("Ошибка удаления:", error);
    }
  };

  return (
    <div>
      <h2>Управление статусами</h2>

      {/* Список статусов */}
      <div>
        {statuses.map((status) => (
          <div
            key={status.value}
            style={{ display: "flex", gap: "10px", padding: "10px" }}
          >
            <span>
              {status.emoji} {status.label}
            </span>
            <span>({status.value})</span>
            {status.is_system && (
              <span style={{ color: "red" }}>Системный</span>
            )}
            {!status.is_system && (
              <button onClick={() => deleteStatus(status.value)}>
                Удалить
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Форма добавления */}
      <div style={{ marginTop: "20px" }}>
        <h3>Добавить новый статус</h3>
        <input
          placeholder="Value (англ, без пробелов)"
          value={newStatus.value}
          onChange={(e) =>
            setNewStatus({ ...newStatus, value: e.target.value })
          }
        />
        <input
          placeholder="Название"
          value={newStatus.label}
          onChange={(e) =>
            setNewStatus({ ...newStatus, label: e.target.value })
          }
        />
        <input
          placeholder="Эмодзи"
          value={newStatus.emoji}
          onChange={(e) =>
            setNewStatus({ ...newStatus, emoji: e.target.value })
          }
        />
        <button onClick={addStatus}>Добавить</button>
      </div>
    </div>
  );
}
```

---

## 🎯 РЕКОМЕНДАЦИИ

### Сообщения бота

1. **Используйте плейсхолдеры** - `{name}`, `{status_name}`, `{admin_name}`
2. **Сохраняйте форматирование** - переносы строк `\n` важны
3. **Тестируйте после изменений** - проверьте бота после обновления
4. **Делайте бэкапы** - сохраняйте текущие значения перед массовыми изменениями

### Статусы клиентов

1. **Не удаляйте системные** - `student` и `reserve` обязательны
2. **Используйте понятные value** - латиница, без пробелов
3. **Добавляйте эмодзи** - они улучшают UX в Telegram
4. **Управляйте порядком** - используйте поле `order` для сортировки
5. **Осторожно с удалением** - проверьте, используется ли статус пользователями

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Системные статусы**: `student` и `reserve` нельзя удалить, только отредактировать label и emoji
2. **Уникальность value**: Нельзя создать два статуса с одинаковым value
3. **Валидация value**: Только буквы, цифры и подчеркивания (латиница)
4. **Плейсхолдеры**: Убедитесь, что плейсхолдеры в сообщениях соответствуют используемым в коде
5. **Кеширование**: Бот читает данные из БД при каждом запросе, изменения применяются сразу

---

## 📚 Связанные документы

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Основная документация API
- [README.md](README.md) - Общая документация проекта
- [REACT_EXAMPLES.md](REACT_EXAMPLES.md) - Примеры React компонентов

---

**Версия:** 2.2.0  
**Последнее обновление:** 12.10.2025
