import React from 'react';
import { Card, Row, Col, Statistic, Button, Space } from 'antd';
import {
    UserOutlined,
    MessageOutlined,
    BookOutlined,
    BranchesOutlined,
    ArrowUpOutlined,
    ArrowDownOutlined
} from '@ant-design/icons';

/**
 * Exemplo de página que funciona com o MainLayout refatorado
 * Demonstra como o conteúdo fica organizado dentro do layout
 */
const ExampleDashboardPage: React.FC = () => {
    return (
        <div style={{ padding: '24px' }}>
            {/* Estatísticas principais */}
            <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="Conversas Ativas"
                            value={12}
                            prefix={<MessageOutlined />}
                            valueStyle={{ color: '#3f8600' }}
                            suffix={<ArrowUpOutlined />}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="Base de Conhecimento"
                            value={145}
                            prefix={<BookOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="Workflows Ativos"
                            value={8}
                            prefix={<BranchesOutlined />}
                            valueStyle={{ color: '#722ed1' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="Usuários Online"
                            value={23}
                            prefix={<UserOutlined />}
                            valueStyle={{ color: '#cf1322' }}
                            suffix={<ArrowDownOutlined />}
                        />
                    </Card>
                </Col>
            </Row>

            {/* Área de ações rápidas */}
            <Card title="Ações Rápidas" style={{ marginBottom: '24px' }}>
                <Space size="middle" wrap>
                    <Button type="primary" icon={<MessageOutlined />}>
                        Novo Chat
                    </Button>
                    <Button icon={<BookOutlined />}>
                        Adicionar Conhecimento
                    </Button>
                    <Button icon={<BranchesOutlined />}>
                        Criar Workflow
                    </Button>
                </Space>
            </Card>

            {/* Conteúdo principal */}
            <Row gutter={[24, 24]}>
                <Col xs={24} lg={16}>
                    <Card title="Atividade Recente">
                        <div style={{ minHeight: '300px', padding: '20px' }}>
                            <p>Lista de atividades recentes apareceria aqui...</p>
                            <p>O MainLayout fornece a estrutura completa:</p>
                            <ul>
                                <li>✅ Sidebar com navegação organizada por grupos</li>
                                <li>✅ Header com informações do usuário e notificações</li>
                                <li>✅ Content area responsiva</li>
                                <li>✅ Menu de usuário com dropdown</li>
                                <li>✅ Integração com React Router</li>
                            </ul>
                        </div>
                    </Card>
                </Col>
                <Col xs={24} lg={8}>
                    <Card title="Status do Sistema">
                        <div style={{ minHeight: '300px', padding: '20px' }}>
                            <p>Informações de status do sistema...</p>
                            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                                <div>
                                    <strong>LLM Status:</strong> <span style={{ color: '#52c41a' }}>✓ Conectado</span>
                                </div>
                                <div>
                                    <strong>MCP Server:</strong> <span style={{ color: '#52c41a' }}>✓ Ativo</span>
                                </div>
                                <div>
                                    <strong>Websocket:</strong> <span style={{ color: '#52c41a' }}>✓ Conectado</span>
                                </div>
                            </Space>
                        </div>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default ExampleDashboardPage;
