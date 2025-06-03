import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { HomeOutlined } from '@ant-design/icons';

interface ErrorBoundaryProps {
  error: Error;
  resetErrorBoundary: () => void;
}

const RouteErrorFallback: React.FC<ErrorBoundaryProps> = ({
  error,
  resetErrorBoundary,
}) => {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate('/');
    resetErrorBoundary();
  };

  return (
    <Result
      status='error'
      title='Erro ao carregar página'
      subTitle={`Desculpe, ocorreu um erro inesperado: ${error.message}`}
      extra={[
        <Button
          type='primary'
          key='home'
          icon={<HomeOutlined />}
          onClick={handleGoHome}
        >
          Voltar ao Início
        </Button>,
        <Button key='retry' onClick={resetErrorBoundary}>
          Tentar Novamente
        </Button>,
      ]}
    />
  );
};

export default RouteErrorFallback;
