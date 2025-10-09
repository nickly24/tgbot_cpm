# Примеры кода для React приложения v2.0

## 🎯 Обновления в v2.0

- ✅ Новые статусы клиентов (студент, абитуриент, родители)
- ✅ Отслеживание непрочитанных сообщений
- ✅ Endpoint для пометки сообщений как прочитанных
- ✅ Статистика по чатам
- ✅ Улучшенная типизация

## Быстрый старт

### 1. Базовый API клиент (обновленный)

```javascript
// services/api.js
const API_BASE_URL = "http://0.0.0.0:80/api";

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "API Error");
      }

      return data;
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  }

  // ========== ЧАТЫ ==========

  // Получить список чатов
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

  // 🆕 Пометить сообщения как прочитанные
  async markAsRead(chatId) {
    return this.request(`/chats/${chatId}/mark-read`, {
      method: "POST",
    });
  }

  // ========== ПОЛЬЗОВАТЕЛИ ==========

  // Получить информацию о пользователе
  async getUserInfo(chatId) {
    return this.request(`/chats/${chatId}/user`);
  }

  // Обновить имя пользователя
  async updateUserName(chatId, name) {
    return this.request(`/chats/${chatId}/name`, {
      method: "PUT",
      body: JSON.stringify({ name }),
    });
  }

  // ========== СТАТУСЫ ==========

  // 🆕 Получить список всех статусов
  async getStatuses() {
    return this.request("/statuses");
  }

  // 🆕 Получить статус пользователя
  async getUserStatus(chatId) {
    return this.request(`/chats/${chatId}/status`);
  }

  // 🆕 Обновить статус пользователя
  async updateUserStatus(chatId, status) {
    return this.request(`/chats/${chatId}/status`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    });
  }

  // ========== СТАТИСТИКА ==========

  // 🆕 Получить общую статистику
  async getStats() {
    return this.request("/stats");
  }

  // Проверка состояния API
  async healthCheck() {
    return this.request("/health");
  }
}

export const apiClient = new ApiClient();
```

### 2. React хуки

```javascript
// hooks/useChats.js
import { useState, useEffect } from "react";
import { apiClient } from "../services/api";

export const useChats = () => {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchChats = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getChats();
      setChats(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChats();

    // Автообновление каждые 10 секунд
    const interval = setInterval(fetchChats, 10000);
    return () => clearInterval(interval);
  }, []);

  return { chats, loading, error, refetch: fetchChats };
};
```

```javascript
// hooks/useChatHistory.js (обновленный)
import { useState, useEffect } from "react";
import { apiClient } from "../services/api";

export const useChatHistory = (chatId) => {
  const [messages, setMessages] = useState([]);
  const [userInfo, setUserInfo] = useState(null);
  const [status, setStatus] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    if (!chatId) return;

    try {
      setLoading(true);
      const response = await apiClient.getChatHistory(chatId);
      setMessages(response.data.messages || []);
      setUserInfo(response.data.user_info);
      setStatus(response.data.status);
      setUnreadCount(response.data.unread_count || 0);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();

    // Автообновление каждые 3 секунды
    const interval = setInterval(fetchHistory, 3000);
    return () => clearInterval(interval);
  }, [chatId]);

  const sendMessage = async (message, adminName) => {
    try {
      await apiClient.sendMessage(chatId, message, adminName);
      // Обновляем историю после отправки
      await fetchHistory();
    } catch (err) {
      setError(err.message);
    }
  };

  return {
    messages,
    userInfo,
    status,
    unreadCount,
    loading,
    error,
    sendMessage,
    refetch: fetchHistory,
  };
};
```

### 3. Основные компоненты

```jsx
// components/ChatList.jsx (обновленный)
import React from "react";
import { useChats } from "../hooks/useChats";
import UnreadBadge from "./UnreadBadge";

const STATUS_LABELS = {
  student: "Студент",
  applicant: "Абитуриент",
  parent_student: "Родитель студента",
  parent_applicant: "Родитель абитуриента",
};

const ChatList = ({ onChatSelect, selectedChatId }) => {
  const { chats, loading, error } = useChats();

  if (loading) return <div>Загрузка чатов...</div>;
  if (error) return <div>Ошибка: {error}</div>;

  return (
    <div className="chat-list">
      <h2>Чаты ({chats.length})</h2>
      {chats.map((chat) => (
        <div
          key={chat.chat_id}
          className={`chat-item ${
            selectedChatId === chat.chat_id ? "selected" : ""
          } ${chat.unread_count > 0 ? "has-unread" : ""}`}
          onClick={() => onChatSelect(chat.chat_id)}
        >
          <div className="chat-header">
            <span className="user-name">
              {chat.user_info?.name || "Неизвестно"}
            </span>
            <div className="chat-badges">
              <span className={`status-badge status-${chat.status}`}>
                {STATUS_LABELS[chat.status] || "Не указан"}
              </span>
              <UnreadBadge count={chat.unread_count} />
            </div>
          </div>
          <div className="last-message">
            {chat.last_message?.text || "Нет сообщений"}
          </div>
          <div className="last-time">
            {chat.updated_at ? new Date(chat.updated_at).toLocaleString() : ""}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChatList;
```

```jsx
// components/ChatWindow.jsx (обновленный)
import React, { useState, useRef, useEffect } from "react";
import { useChatHistory } from "../hooks/useChatHistory";
import { apiClient } from "../services/api";

const STATUS_LABELS = {
  student: "Студент",
  applicant: "Абитуриент",
  parent_student: "Родитель студента",
  parent_applicant: "Родитель абитуриента",
};

const ChatWindow = ({ chatId, onMessagesRead }) => {
  const {
    messages,
    userInfo,
    status,
    loading,
    error,
    sendMessage,
    unreadCount,
  } = useChatHistory(chatId);
  const [newMessage, setNewMessage] = useState("");
  const [adminName, setAdminName] = useState("Администратор");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 🆕 Автоматически помечать сообщения как прочитанные при открытии чата
  useEffect(() => {
    const markAsRead = async () => {
      if (chatId && unreadCount > 0) {
        try {
          await apiClient.markAsRead(chatId);
          // Уведомить родительский компонент об обновлении
          if (onMessagesRead) {
            onMessagesRead();
          }
        } catch (error) {
          console.error("Ошибка пометки как прочитанное:", error);
        }
      }
    };

    // Помечать как прочитанное через 1 секунду после открытия
    const timer = setTimeout(markAsRead, 1000);
    return () => clearTimeout(timer);
  }, [chatId, unreadCount, onMessagesRead]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    await sendMessage(newMessage, adminName);
    setNewMessage("");
  };

  if (loading) return <div>Загрузка сообщений...</div>;
  if (error) return <div>Ошибка: {error}</div>;
  if (!chatId) return <div>Выберите чат</div>;

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="user-details">
          <h3>{userInfo?.name || "Неизвестно"}</h3>
          <span className="username">@{userInfo?.username}</span>
        </div>
        <span className={`status-badge status-${status}`}>
          {STATUS_LABELS[status] || "Не указан"}
        </span>
      </div>

      <div className="messages-container">
        {messages.map((msg) => (
          <div
            key={msg._id}
            className={`message ${
              msg.from_user ? "user-message" : "admin-message"
            } ${msg.from_user && !msg.is_read ? "unread" : ""}`}
          >
            <div className="message-header">
              <span className="sender">
                {msg.from_user
                  ? userInfo?.name
                  : msg.admin_name || "Администратор"}
              </span>
              <span className="timestamp">
                {new Date(msg.timestamp).toLocaleString()}
              </span>
              {/* 🆕 Индикатор непрочитанного сообщения */}
              {msg.from_user && !msg.is_read && (
                <span className="unread-indicator">●</span>
              )}
            </div>
            <div className="message-text">{msg.text}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="message-form">
        <input
          type="text"
          value={adminName}
          onChange={(e) => setAdminName(e.target.value)}
          placeholder="Ваше имя"
          className="admin-name-input"
        />
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Введите сообщение..."
          className="message-input"
        />
        <button type="submit" disabled={!newMessage.trim()}>
          Отправить
        </button>
      </form>
    </div>
  );
};

export default ChatWindow;
```

```jsx
// components/UserInfo.jsx
import React, { useState } from "react";
import { apiClient } from "../services/api";

const UserInfo = ({ userInfo, chatId, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [newName, setNewName] = useState(userInfo?.name || "");
  const [loading, setLoading] = useState(false);

  const handleUpdateName = async () => {
    if (!newName.trim()) return;

    setLoading(true);
    try {
      await apiClient.updateUserName(chatId, newName);
      onUpdate();
      setIsEditing(false);
    } catch (error) {
      console.error("Ошибка обновления имени:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!userInfo) return null;

  return (
    <div className="user-info">
      <h4>Информация о пользователе</h4>

      <div className="info-item">
        <label>ID:</label>
        <span>{userInfo.user_id}</span>
      </div>

      <div className="info-item">
        <label>Username:</label>
        <span>@{userInfo.username}</span>
      </div>

      <div className="info-item">
        <label>Имя:</label>
        {isEditing ? (
          <div className="edit-name">
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              disabled={loading}
            />
            <button onClick={handleUpdateName} disabled={loading}>
              {loading ? "Сохранение..." : "Сохранить"}
            </button>
            <button onClick={() => setIsEditing(false)}>Отмена</button>
          </div>
        ) : (
          <div className="name-display">
            <span>{userInfo.name}</span>
            <button onClick={() => setIsEditing(true)}>Изменить</button>
          </div>
        )}
      </div>

      <div className="info-item">
        <label>Дата регистрации:</label>
        <span>{new Date(userInfo.created_at).toLocaleString()}</span>
      </div>
    </div>
  );
};

export default UserInfo;
```

```jsx
// 🆕 components/StatusSelector.jsx
import React, { useState, useEffect } from "react";
import { apiClient } from "../services/api";

const STATUS_COLORS = {
  student: "#4CAF50",
  applicant: "#2196F3",
  parent_student: "#FF9800",
  parent_applicant: "#9C27B0",
};

const StatusSelector = ({ currentStatus, chatId, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [statuses, setStatuses] = useState([]);

  useEffect(() => {
    // Загружаем список статусов
    const fetchStatuses = async () => {
      try {
        const response = await apiClient.getStatuses();
        setStatuses(response.data);
      } catch (error) {
        console.error("Ошибка загрузки статусов:", error);
      }
    };

    fetchStatuses();
  }, []);

  const handleStatusChange = async (status) => {
    setLoading(true);
    try {
      await apiClient.updateUserStatus(chatId, status);
      onUpdate();
    } catch (error) {
      console.error("Ошибка обновления статуса:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="status-selector">
      <h4>Статус клиента</h4>
      <div className="status-options">
        {statuses.map((status) => (
          <button
            key={status.value}
            className={`status-option ${
              currentStatus === status.value ? "active" : ""
            }`}
            onClick={() => handleStatusChange(status.value)}
            disabled={loading}
            style={{ backgroundColor: STATUS_COLORS[status.value] }}
          >
            {status.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default StatusSelector;
```

```jsx
// 🆕 components/UnreadBadge.jsx
import React from "react";

const UnreadBadge = ({ count }) => {
  if (count === 0) return null;

  return <span className="unread-badge">{count > 99 ? "99+" : count}</span>;
};

export default UnreadBadge;
```

```jsx
// 🆕 components/StatsDashboard.jsx
import React, { useState, useEffect } from "react";
import { apiClient } from "../services/api";

const StatsDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiClient.getStats();
        setStats(response.data);
      } catch (error) {
        console.error("Ошибка загрузки статистики:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    // Обновлять каждую минуту
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Загрузка статистики...</div>;
  if (!stats) return null;

  return (
    <div className="stats-dashboard">
      <h3>Статистика</h3>

      <div className="stat-card">
        <div className="stat-value">{stats.total_chats}</div>
        <div className="stat-label">Всего чатов</div>
      </div>

      <div className="stat-card highlight">
        <div className="stat-value">{stats.total_unread_messages}</div>
        <div className="stat-label">Непрочитанных сообщений</div>
      </div>

      <div className="stat-breakdown">
        <h4>По статусам:</h4>
        {Object.entries(stats.status_distribution).map(([status, count]) => (
          <div key={status} className="status-stat">
            <span className="status-name">{status}</span>
            <span className="status-count">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatsDashboard;
```

### 4. Главный компонент приложения

```jsx
// App.jsx
import React, { useState } from 'react';
import ChatList from './components/ChatList';
import ChatWindow from './components/ChatWindow';
import UserInfo from './components/UserInfo';
import ThemeSelector from './components/ThemeSelector';
import './App.css';

function App() {
  const [selectedChatId, setSelectedChatId] = useState(null);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Telegram Bot Admin Panel</h1>
      </header>

      <div className="app-content">
        <div className="sidebar">
          <ChatList
            onChatSelect={setSelectedChatId}
            selectedChatId={selectedChatId}
          />
        </div>

        <div className="main-content">
          <div className="chat-section">
            <ChatWindow chatId={selectedChatId} />
          </div>

          <div className="info-section">
            <UserInfo
              userInfo={selectedChatId ? /* получить из хука */ : null}
              chatId={selectedChatId}
              onUpdate={() => {/* обновить данные */}}
            />
            <ThemeSelector
              currentTheme={selectedChatId ? /* получить из хука */ : 'new'}
              chatId={selectedChatId}
              onUpdate={() => {/* обновить данные */}}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
```

### 5. Базовые стили CSS

```css
/* App.css */
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-header {
  background: #2c3e50;
  color: white;
  padding: 1rem;
  text-align: center;
}

.app-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  background: #ecf0f1;
  border-right: 1px solid #bdc3c7;
  overflow-y: auto;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.info-section {
  width: 250px;
  background: #f8f9fa;
  border-left: 1px solid #bdc3c7;
  padding: 1rem;
  overflow-y: auto;
}

.chat-list {
  padding: 1rem;
}

.chat-item {
  padding: 1rem;
  border-bottom: 1px solid #bdc3c7;
  cursor: pointer;
  transition: background-color 0.2s;
}

.chat-item:hover {
  background: #d5dbdb;
}

.chat-item.selected {
  background: #3498db;
  color: white;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.theme-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.theme-new {
  background: #4caf50;
  color: white;
}
.theme-support {
  background: #2196f3;
  color: white;
}
.theme-sales {
  background: #ff9800;
  color: white;
}
.theme-technical {
  background: #9c27b0;
  color: white;
}
.theme-urgent {
  background: #f44336;
  color: white;
}

.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-container {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: #f8f9fa;
}

.message {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  max-width: 70%;
}

.user-message {
  background: #e3f2fd;
  margin-left: 0;
}

.admin-message {
  background: #e8f5e8;
  margin-left: auto;
}

.message-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.message-form {
  display: flex;
  padding: 1rem;
  background: white;
  border-top: 1px solid #bdc3c7;
}

.message-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  margin-right: 0.5rem;
}

.admin-name-input {
  width: 150px;
  padding: 0.5rem;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  margin-right: 0.5rem;
}

.user-info,
.theme-selector {
  margin-bottom: 2rem;
}

.info-item {
  margin-bottom: 1rem;
}

.info-item label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.theme-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.theme-option {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: opacity 0.2s;
}

.theme-option:hover {
  opacity: 0.8;
}

.theme-option.active {
  box-shadow: 0 0 0 2px #333;
}
```

## Установка и запуск

1. Создайте новый React проект:

```bash
npx create-react-app telegram-bot-admin
cd telegram-bot-admin
```

2. Установите зависимости:

```bash
npm install
```

3. Скопируйте файлы из примеров выше

4. Запустите приложение:

```bash
npm start
```

5. Убедитесь, что ваш Telegram Bot API сервер запущен на `http://0.0.0.0:80`

## Дополнительные возможности

### Поиск и фильтрация чатов

```javascript
// hooks/useChatFilter.js
import { useState, useMemo } from "react";

export const useChatFilter = (chats) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [themeFilter, setThemeFilter] = useState("all");

  const filteredChats = useMemo(() => {
    return chats.filter((chat) => {
      const matchesSearch =
        chat.user_info?.name
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        chat.user_info?.username
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase());
      const matchesTheme = themeFilter === "all" || chat.theme === themeFilter;

      return matchesSearch && matchesTheme;
    });
  }, [chats, searchTerm, themeFilter]);

  return {
    filteredChats,
    searchTerm,
    setSearchTerm,
    themeFilter,
    setThemeFilter,
  };
};
```

### Уведомления о новых сообщениях

```javascript
// hooks/useNotifications.js
import { useEffect } from "react";

export const useNotifications = (chats) => {
  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  }, []);

  const showNotification = (title, body) => {
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(title, { body });
    }
  };

  // Отслеживание новых сообщений
  useEffect(() => {
    const lastMessageTimes = {};

    const checkNewMessages = () => {
      chats.forEach((chat) => {
        if (chat.last_message_time) {
          const lastTime = lastMessageTimes[chat.chat_id];
          if (
            lastTime &&
            new Date(chat.last_message_time) > new Date(lastTime)
          ) {
            showNotification(
              `Новое сообщение от ${chat.user_info?.name}`,
              chat.last_message?.text || "Новое сообщение"
            );
          }
          lastMessageTimes[chat.chat_id] = chat.last_message_time;
        }
      });
    };

    const interval = setInterval(checkNewMessages, 5000);
    return () => clearInterval(interval);
  }, [chats]);
};
```

Эти примеры дают полную основу для создания React приложения для управления Telegram ботом!
