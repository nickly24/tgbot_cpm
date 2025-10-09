# 🔧 Функции для администратора

## 1️⃣ Изменение статуса клиента

**Endpoint:** `PUT /api/chats/<chat_id>/status`

**Описание:** Администратор может изменить статус клиента (студент, абитуриент, родитель и т.д.)

**Пример запроса:**

```bash
curl -X PUT http://0.0.0.0:80/api/chats/672621804/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "applicant"
  }'
```

**Доступные статусы:**

- `student` - Студент
- `applicant` - Абитуриент
- `parent_student` - Родитель студента
- `parent_applicant` - Родитель абитуриента

**Ответ:**

```json
{
  "success": true,
  "message": "Статус пользователя обновлен успешно",
  "status_name": "Абитуриент"
}
```

---

## 2️⃣ Пометка сообщений как прочитанные

**Endpoint:** `POST /api/chats/<chat_id>/mark-read`

**Описание:** Помечает все непрочитанные сообщения от клиента как прочитанные. Вызывайте этот endpoint когда администратор открывает чат.

**Пример запроса:**

```bash
curl -X POST http://0.0.0.0:80/api/chats/672621804/mark-read
```

**Ответ:**

```json
{
  "success": true,
  "message": "Помечено как прочитано: 5 сообщений",
  "marked_count": 5
}
```

**Когда использовать:**

- Когда администратор открывает чат
- После прочтения новых сообщений
- Можно вызывать автоматически при открытии чата в админке

---

## 3️⃣ Массовая рассылка

**Endpoint:** `POST /api/broadcast`

**Описание:** Отправляет сообщение всем пользователям с указанными статусами. Можно отправить всем или выборочно.

### Отправить ВСЕМ пользователям:

```bash
curl -X POST http://0.0.0.0:80/api/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Уважаемые пользователи! Завтра выходной день.",
    "admin_name": "Администрация"
  }'
```

### Отправить только СТУДЕНТАМ:

```bash
curl -X POST http://0.0.0.0:80/api/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Студентам: завтра экзамен в 10:00!",
    "statuses": ["student"],
    "admin_name": "Деканат"
  }'
```

### Отправить СТУДЕНТАМ и АБИТУРИЕНТАМ:

```bash
curl -X POST http://0.0.0.0:80/api/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Важное объявление для студентов и абитуриентов!",
    "statuses": ["student", "applicant"],
    "admin_name": "Приемная комиссия"
  }'
```

### Отправить только РОДИТЕЛЯМ:

```bash
curl -X POST http://0.0.0.0:80/api/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Уважаемые родители! Приглашаем на родительское собрание.",
    "statuses": ["parent_student", "parent_applicant"]
  }'
```

**Параметры:**

- `message` (обязательно) - текст сообщения
- `statuses` (опционально) - массив статусов. Если не указан - отправляется всем
- `admin_name` (опционально) - имя отправителя (по умолчанию "Администратор")

**Ответ:**

```json
{
  "success": true,
  "message": "Рассылка завершена",
  "stats": {
    "total_target": 25,
    "success": 24,
    "failed": 1,
    "failed_chats": [123456789]
  }
}
```

**Статистика рассылки:**

- `total_target` - сколько пользователей подходит под критерии
- `success` - успешно отправлено
- `failed` - не удалось отправить
- `failed_chats` - ID чатов, куда не получилось отправить

---

## 💡 Примеры использования в JavaScript

### 1. Изменение статуса

```javascript
async function changeStatus(chatId, newStatus) {
  const response = await fetch(`http://0.0.0.0:80/api/chats/${chatId}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus }),
  });

  const data = await response.json();
  if (data.success) {
    console.log(`Статус изменен на: ${data.status_name}`);
  }
}

// Использование
changeStatus(672621804, "student");
```

### 2. Пометить как прочитанное

```javascript
async function markAsRead(chatId) {
  const response = await fetch(
    `http://0.0.0.0:80/api/chats/${chatId}/mark-read`,
    {
      method: "POST",
    }
  );

  const data = await response.json();
  if (data.success) {
    console.log(`Прочитано ${data.marked_count} сообщений`);
  }
}

// Автоматически при открытии чата
function openChat(chatId) {
  // Загружаем историю
  loadChatHistory(chatId);

  // Помечаем как прочитанное
  markAsRead(chatId);
}
```

### 3. Массовая рассылка

```javascript
async function sendBroadcast(
  message,
  statuses = null,
  adminName = "Администратор"
) {
  const body = {
    message: message,
    admin_name: adminName,
  };

  // Если указаны статусы - добавляем
  if (statuses) {
    body.statuses = statuses;
  }

  const response = await fetch("http://0.0.0.0:80/api/broadcast", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await response.json();
  if (data.success) {
    console.log(
      `Отправлено: ${data.stats.success} из ${data.stats.total_target}`
    );
  }
  return data;
}

// Примеры использования:

// Отправить всем
sendBroadcast("Общее объявление для всех!");

// Только студентам
sendBroadcast("Завтра экзамен!", ["student"], "Деканат");

// Студентам и абитуриентам
sendBroadcast("Важная информация!", ["student", "applicant"]);

// Только родителям
sendBroadcast("Родительское собрание", ["parent_student", "parent_applicant"]);
```

---

## ⚠️ Важные замечания

### Для пометки как прочитанное:

- Вызывайте автоматически при открытии чата администратором
- Обновляет только сообщения от клиента (from_user=true)
- Сообщения от админа всегда считаются "прочитанными"

### Для массовой рассылки:

- Если `statuses` не указан - отправляется **всем** пользователям с выбранным статусом
- Пользователи без статуса не получат рассылку
- Рассылка может занять время при большом количестве пользователей
- Неуспешные отправки (бот заблокирован) не останавливают рассылку

### Для смены статуса:

- Можно менять статус в любой момент
- После смены статуса пользователь попадает в новую группу для рассылок
- Валидация - только допустимые статусы

---

## 📊 React компоненты

### Компонент смены статуса

```jsx
function StatusChanger({ chatId, currentStatus, onUpdate }) {
  const [loading, setLoading] = useState(false);

  const statuses = [
    { value: "student", label: "Студент" },
    { value: "applicant", label: "Абитуриент" },
    { value: "parent_student", label: "Родитель студента" },
    { value: "parent_applicant", label: "Родитель абитуриента" },
  ];

  const handleChange = async (newStatus) => {
    setLoading(true);
    try {
      await fetch(`/api/chats/${chatId}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      onUpdate();
    } finally {
      setLoading(false);
    }
  };

  return (
    <select
      value={currentStatus}
      onChange={(e) => handleChange(e.target.value)}
      disabled={loading}
    >
      {statuses.map((s) => (
        <option key={s.value} value={s.value}>
          {s.label}
        </option>
      ))}
    </select>
  );
}
```

### Компонент массовой рассылки

```jsx
function BroadcastPanel() {
  const [message, setMessage] = useState("");
  const [selectedStatuses, setSelectedStatuses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const statuses = [
    "student",
    "applicant",
    "parent_student",
    "parent_applicant",
  ];

  const handleSend = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/broadcast", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          statuses: selectedStatuses.length > 0 ? selectedStatuses : undefined,
        }),
      });
      const data = await response.json();
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Массовая рассылка</h3>

      <div>
        <label>Кому отправить:</label>
        {statuses.map((status) => (
          <label key={status}>
            <input
              type="checkbox"
              checked={selectedStatuses.includes(status)}
              onChange={(e) => {
                if (e.target.checked) {
                  setSelectedStatuses([...selectedStatuses, status]);
                } else {
                  setSelectedStatuses(
                    selectedStatuses.filter((s) => s !== status)
                  );
                }
              }}
            />
            {status}
          </label>
        ))}
        {selectedStatuses.length === 0 && <em>(Будет отправлено всем)</em>}
      </div>

      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Текст сообщения..."
        rows={5}
      />

      <button onClick={handleSend} disabled={loading || !message}>
        {loading ? "Отправка..." : "Отправить рассылку"}
      </button>

      {result && (
        <div>
          <h4>Результат:</h4>
          <p>Успешно: {result.stats?.success}</p>
          <p>Ошибок: {result.stats?.failed}</p>
        </div>
      )}
    </div>
  );
}
```

---

**Версия:** 2.0.0  
**Дата:** 09.10.2025
