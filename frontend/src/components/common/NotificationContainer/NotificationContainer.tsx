// Notification component for displaying system notifications
import React from "react";
import { useNotifications } from "../../../hooks/useWebSocket";
import "./NotificationContainer.css";

interface NotificationProps {
  notification: {
    id: string;
    type: "success" | "error" | "warning" | "info";
    title: string;
    message: string;
    timestamp: string;
    read: boolean;
  };
  onClear: (id: string) => void;
}

const Notification: React.FC<NotificationProps> = ({
  notification,
  onClear,
}) => {
  const getIcon = () => {
    switch (notification.type) {
      case "success":
        return "✅";
      case "error":
        return "❌";
      case "warning":
        return "⚠️";
      case "info":
      default:
        return "ℹ️";
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  return (
    <div className={`notification notification--${notification.type}`}>
      <div className="notification__header">
        <span className="notification__icon">{getIcon()}</span>
        <span className="notification__title">{notification.title}</span>
        <span className="notification__time">
          {formatTime(notification.timestamp)}
        </span>
        <button
          className="notification__close"
          onClick={() => onClear(notification.id)}
          aria-label="Close notification"
        >
          ×
        </button>
      </div>
      <div className="notification__message">{notification.message}</div>
    </div>
  );
};

const NotificationContainer: React.FC = () => {
  const { notifications, dismissNotification, clearAllNotifications } =
    useNotifications();

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="notification-container">
      <div className="notification-container__header">
        <h3>Notifications</h3>
        {notifications.length > 1 && (
          <button
            className="notification-container__clear-all"
            onClick={clearAllNotifications}
          >
            Clear All
          </button>
        )}
      </div>
      <div className="notification-container__list">
        {notifications.map((notification) => (
          <Notification
            key={notification.id}
            notification={notification}
            onClear={dismissNotification}
          />
        ))}
      </div>
    </div>
  );
};

export default NotificationContainer;
