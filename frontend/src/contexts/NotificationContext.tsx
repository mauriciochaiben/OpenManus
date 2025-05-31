import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { notification } from 'antd';
import {
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    InfoCircleOutlined,
    WarningOutlined
} from '@ant-design/icons';
import { eventBus } from '../utils/eventBus';

export interface NotificationData {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    taskId?: string;
    timestamp: string;
}

interface NotificationContextType {
    notifications: NotificationData[];
    addNotification: (notification: Omit<NotificationData, 'id' | 'timestamp'>) => void;
    removeNotification: (id: string) => void;
    clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotifications must be used within a NotificationProvider');
    }
    return context;
};

interface NotificationProviderProps {
    children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
    const [notifications, setNotifications] = useState<NotificationData[]>([]);
    const [api, contextHolder] = notification.useNotification();

    const addNotification = (notificationData: Omit<NotificationData, 'id' | 'timestamp'>) => {
        const newNotification: NotificationData = {
            ...notificationData,
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
        };

        setNotifications(prev => [newNotification, ...prev.slice(0, 99)]); // Keep only last 100

        // Show Ant Design notification
        const config = {
            message: newNotification.title,
            description: newNotification.message,
            duration: 4.5,
            icon: getNotificationIcon(newNotification.type),
        };

        switch (newNotification.type) {
            case 'success':
                api.success(config);
                break;
            case 'error':
                api.error({ ...config, duration: 8 });
                break;
            case 'warning':
                api.warning(config);
                break;
            default:
                api.info(config);
        }
    };

    const removeNotification = (id: string) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    const clearAll = () => {
        setNotifications([]);
    };

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'success':
                return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
            case 'error':
                return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
            case 'warning':
                return <WarningOutlined style={{ color: '#faad14' }} />;
            default:
                return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
        }
    };

    useEffect(() => {
        // Listen for task completion notifications using EventBus
        const unsubTaskUpdate = eventBus.on('task:updated', (data: any) => {
            if (data.task?.status === 'completed') {
                addNotification({
                    type: 'success',
                    title: 'Task Completed',
                    message: `Task "${data.task.title}" has been completed successfully!`,
                    taskId: data.task.id,
                });
            } else if (data.task?.status === 'error') {
                addNotification({
                    type: 'error',
                    title: 'Task Failed',
                    message: `Task "${data.task.title}" encountered an error.`,
                    taskId: data.task.id,
                });
            }
        });

        // Listen for step notifications
        const unsubStepUpdate = eventBus.on('task:stepUpdated', (data: any) => {
            if (data.step?.status === 'completed') {
                addNotification({
                    type: 'info',
                    title: 'Step Completed',
                    message: `Step "${data.step.title}" has been completed.`,
                    taskId: data.taskId,
                });
            } else if (data.step?.status === 'error') {
                addNotification({
                    type: 'warning',
                    title: 'Step Failed',
                    message: `Step "${data.step.title}" encountered an error.`,
                    taskId: data.taskId,
                });
            }
        });

        // Listen for general system notifications
        const unsubNotification = eventBus.on('system:notification', (data: any) => {
            addNotification({
                type: data.type || 'info',
                title: data.title || 'System Notification',
                message: data.message,
                taskId: data.taskId,
            });
        });

        // Listen for WebSocket connection events
        const unsubConnected = eventBus.on('websocket:connected', () => {
            addNotification({
                type: 'success',
                title: 'Connected',
                message: 'Real-time updates are now active.',
            });
        });

        const unsubDisconnected = eventBus.on('websocket:disconnected', () => {
            addNotification({
                type: 'warning',
                title: 'Disconnected',
                message: 'Real-time updates are temporarily unavailable.',
            });
        });

        const unsubError = eventBus.on('websocket:error', () => {
            addNotification({
                type: 'error',
                title: 'Connection Error',
                message: 'Failed to connect to real-time services.',
            });
        });

        return () => {
            unsubTaskUpdate();
            unsubStepUpdate();
            unsubNotification();
            unsubConnected();
            unsubDisconnected();
            unsubError();
        };
    }, []);

    const value: NotificationContextType = {
        notifications,
        addNotification,
        removeNotification,
        clearAll,
    };

    return (
        <NotificationContext.Provider value={value}>
            {contextHolder}
            {children}
        </NotificationContext.Provider>
    );
};
