import React from 'react';
import { Typography, Card } from 'antd';

const { Title } = Typography;

const SimpleHome: React.FC = () => {
    return (
        <div style={{ padding: '24px' }}>
            <Card>
                <Title level={2}>OpenManus - Sistema Funcionando</Title>
                <p>Se você está vendo esta mensagem, o frontend está carregando corretamente!</p>
            </Card>
        </div>
    );
};

export default SimpleHome;
