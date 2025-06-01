import React, { Suspense } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import LoadingFallback from './LoadingFallback';
import RouteErrorFallback from './RouteErrorFallback';

interface LazyRouteWrapperProps {
    children: React.ReactNode;
    loadingMessage?: string;
}

const LazyRouteWrapper: React.FC<LazyRouteWrapperProps> = ({
    children,
    loadingMessage
}) => {
    return (
        <ErrorBoundary FallbackComponent={RouteErrorFallback}>
            <Suspense fallback={<LoadingFallback message={loadingMessage} />}>
                {children}
            </Suspense>
        </ErrorBoundary>
    );
};

export default LazyRouteWrapper;
