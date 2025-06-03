import React from 'react';
import { Result, Button } from 'antd';
import { ReloadOutlined, HomeOutlined } from '@ant-design/icons';

interface FeatureErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  featureName?: string;
}

interface FeatureErrorBoundaryProps {
  featureName: string;
  children: React.ReactNode;
}

/**
 * Error boundary específico para features
 * Fornece contexto sobre qual feature falhou
 */
class FeatureErrorBoundary extends React.Component<
  FeatureErrorBoundaryProps,
  FeatureErrorBoundaryState
> {
  constructor(props: FeatureErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): FeatureErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error(
      `Error in feature "${this.props.featureName}":`,
      error,
      errorInfo
    );
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <Result
          status='error'
          title={`Erro na feature ${this.props.featureName}`}
          subTitle='Algo deu errado ao carregar esta funcionalidade. Tente recarregar a página ou voltar ao início.'
          extra={[
            <Button
              type='primary'
              icon={<ReloadOutlined />}
              onClick={this.handleReload}
              key='reload'
            >
              Recarregar Página
            </Button>,
            <Button
              icon={<HomeOutlined />}
              onClick={this.handleGoHome}
              key='home'
            >
              Voltar ao Início
            </Button>,
          ]}
        />
      );
    }

    return this.props.children;
  }
}

export default FeatureErrorBoundary;
