import React, { useEffect, useState } from 'react';
import { notification } from 'antd';
import {
    RocketOutlined,
    CheckCircleOutlined,
    LoadingOutlined
} from '@ant-design/icons';

interface LazyLoadEvent {
    componentName: string;
    loadTime: number;
    chunkSize?: number;
}

const LazyLoadIndicator: React.FC = () => {
    const [loadedComponents, setLoadedComponents] = useState<LazyLoadEvent[]>([]);

    useEffect(() => {
        // Monitorar eventos de carregamento lazy
        const handleChunkLoad = (event: CustomEvent<LazyLoadEvent>) => {
            const { componentName, loadTime } = event.detail;

            setLoadedComponents(prev => [...prev, event.detail]);

            // Mostrar notificação apenas em desenvolvimento
            if (process.env.NODE_ENV === 'development') {
                notification.success({
                    message: 'Componente Carregado',
                    description: `${componentName} carregado em ${loadTime}ms`,
                    placement: 'bottomRight',
                    duration: 2,
                    icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />
                });
            }
        };

        // Escutar eventos customizados de lazy loading
        window.addEventListener('lazy-component-loaded', handleChunkLoad as EventListener);

        return () => {
            window.removeEventListener('lazy-component-loaded', handleChunkLoad as EventListener);
        };
    }, []);

    return null; // Componente apenas para efeitos colaterais
};

export default LazyLoadIndicator;

// Utility function para disparar eventos de carregamento
export const reportLazyLoad = (componentName: string, startTime: number) => {
    const loadTime = performance.now() - startTime;

    const event = new CustomEvent('lazy-component-loaded', {
        detail: {
            componentName,
            loadTime: Math.round(loadTime)
        }
    });

    window.dispatchEvent(event);

    // Log para desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        console.log(`🚀 Lazy loaded: ${componentName} (${Math.round(loadTime)}ms)`);
    }
};
