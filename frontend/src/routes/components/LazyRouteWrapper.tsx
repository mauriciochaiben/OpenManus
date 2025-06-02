import React, { Suspense, useEffect, useRef } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import LoadingFallback from './LoadingFallback';
import RouteErrorFallback from './RouteErrorFallback';
import { reportLazyLoad } from '../../components/common/LazyLoadIndicator';

interface LazyRouteWrapperProps {
    children: React.ReactNode;
    loadingMessage?: string;
    componentName?: string;
}

const LazyRouteWrapper: React.FC<LazyRouteWrapperProps> = ({
    children,
    loadingMessage,
    componentName
}) => {
    const startTimeRef = useRef<number>(performance.now());

    useEffect(() => {
        // Reportar carregamento quando o componente for montado
        if (componentName) {
            reportLazyLoad(componentName, startTimeRef.current);
        }
    }, [componentName]);

    return (
        <ErrorBoundary FallbackComponent={RouteErrorFallback}>
            <Suspense fallback={<LoadingFallback message={loadingMessage} />}>
                {children}
            </Suspense>
        </ErrorBoundary>
    );
};

export default LazyRouteWrapper;
