import React from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Input,
  Select,
  Badge,
  Typography,
  Space,
  Divider,
  Tabs,
} from 'antd';
import {
  ThunderboltOutlined,
  StarOutlined,
  HeartOutlined,
  LikeOutlined,
  SettingOutlined,
  UserOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { useTheme } from '../theme';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

/**
 * Página de demonstração do tema customizado
 * Mostra diferentes componentes com o tema aplicado
 */
const ThemeDemoPage: React.FC = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  const tabItems = [
    {
      key: '1',
      label: 'Componentes Básicos',
      children: (
        <div style={{ padding: '24px' }}>
          <Row gutter={[24, 24]}>
            <Col xs={24} md={12}>
              <Card title='Botões' className='openManus-card'>
                <Space
                  direction='vertical'
                  size='middle'
                  style={{ width: '100%' }}
                >
                  <Button type='primary' className='openManus-btn-primary'>
                    Primário
                  </Button>
                  <Button>Padrão</Button>
                  <Button type='dashed'>Tracejado</Button>
                  <Button type='text'>Texto</Button>
                  <Button danger>Perigo</Button>
                </Space>
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title='Inputs' className='openManus-card'>
                <Space
                  direction='vertical'
                  size='middle'
                  style={{ width: '100%' }}
                >
                  <Input
                    placeholder='Input normal'
                    className='openManus-input'
                  />
                  <Input.Password
                    placeholder='Senha'
                    className='openManus-input'
                  />
                  <Select
                    placeholder='Selecione uma opção'
                    style={{ width: '100%' }}
                  >
                    <Option value='1'>Opção 1</Option>
                    <Option value='2'>Opção 2</Option>
                    <Option value='3'>Opção 3</Option>
                  </Select>
                </Space>
              </Card>
            </Col>
          </Row>
        </div>
      ),
    },
    {
      key: '2',
      label: 'Badges e Ícones',
      children: (
        <div style={{ padding: '24px' }}>
          <Row gutter={[24, 24]}>
            <Col xs={24} md={12}>
              <Card title='Badges' className='openManus-card'>
                <Space size='large' wrap>
                  <Badge count={5}>
                    <Button icon={<UserOutlined />}>Usuários</Button>
                  </Badge>
                  <Badge count={0} showZero>
                    <Button icon={<HomeOutlined />}>Home</Button>
                  </Badge>
                  <Badge status='success' text='Ativo' />
                  <Badge status='error' text='Erro' />
                  <Badge status='warning' text='Aviso' />
                </Space>
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title='Ícones' className='openManus-card'>
                <Space size='large' wrap>
                  <ThunderboltOutlined
                    style={{ fontSize: '24px', color: '#1890ff' }}
                  />
                  <StarOutlined
                    style={{ fontSize: '24px', color: '#faad14' }}
                  />
                  <HeartOutlined
                    style={{ fontSize: '24px', color: '#ff4d4f' }}
                  />
                  <LikeOutlined
                    style={{ fontSize: '24px', color: '#52c41a' }}
                  />
                  <SettingOutlined
                    style={{ fontSize: '24px', color: '#722ed1' }}
                  />
                </Space>
              </Card>
            </Col>
          </Row>
        </div>
      ),
    },
    {
      key: '3',
      label: 'Tipografia',
      children: (
        <div style={{ padding: '24px' }}>
          <Card title='Tipografia' className='openManus-card'>
            <Space direction='vertical' size='large' style={{ width: '100%' }}>
              <div>
                <Title level={1}>Título H1</Title>
                <Title level={2}>Título H2</Title>
                <Title level={3}>Título H3</Title>
                <Title level={4}>Título H4</Title>
                <Title level={5}>Título H5</Title>
              </div>
              <Divider />
              <div>
                <Paragraph>
                  Este é um parágrafo normal demonstrando como o texto fica com
                  o tema customizado do OpenManus. O tema foi projetado para ser
                  moderno, limpo e acessível.
                </Paragraph>
                <Text type='secondary'>Texto secundário</Text>
                <br />
                <Text type='success'>Texto de sucesso</Text>
                <br />
                <Text type='warning'>Texto de aviso</Text>
                <br />
                <Text type='danger'>Texto de erro</Text>
                <br />
                <Text disabled>Texto desabilitado</Text>
                <br />
                <Text mark>Texto marcado</Text>
                <br />
                <Text code>Código inline</Text>
                <br />
                <Text keyboard>Ctrl+C</Text>
                <br />
                <Text underline>Texto sublinhado</Text>
                <br />
                <Text delete>Texto deletado</Text>
                <br />
                <Text strong>Texto em negrito</Text>
              </div>
            </Space>
          </Card>
        </div>
      ),
    },
  ];

  return (
    <div className='openManus-fade-in-up' style={{ padding: '24px' }}>
      {/* Header da página */}
      <div style={{ marginBottom: '32px', textAlign: 'center' }}>
        <Title level={2} className='openManus-header-title'>
          🎨 Demonstração do Tema OpenManus
        </Title>
        <Paragraph>
          Explore os componentes com o tema customizado. Teste a troca entre
          tema claro e escuro usando o botão no header.
        </Paragraph>

        <Space size='large'>
          <Button
            type='primary'
            onClick={toggleTheme}
            className='openManus-btn-primary'
          >
            {isDarkMode ? '☀️ Tema Claro' : '🌙 Tema Escuro'}
          </Button>
          <Badge
            count={isDarkMode ? 'Escuro' : 'Claro'}
            style={{
              backgroundColor: isDarkMode ? '#1890ff' : '#52c41a',
              borderRadius: '12px',
              fontSize: '12px',
            }}
          />
        </Space>
      </div>

      {/* Status do tema atual */}
      <Row gutter={[24, 24]} style={{ marginBottom: '32px' }}>
        <Col xs={24} lg={8}>
          <Card className='openManus-card openManus-shadow'>
            <div style={{ textAlign: 'center' }}>
              <ThunderboltOutlined
                style={{
                  fontSize: '48px',
                  color: '#1890ff',
                  marginBottom: '16px',
                }}
              />
              <Title level={4}>Tema Ativo</Title>
              <Text style={{ fontSize: '18px' }}>
                {isDarkMode ? 'Modo Escuro' : 'Modo Claro'}
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card className='openManus-card openManus-shadow'>
            <div style={{ textAlign: 'center' }}>
              <StarOutlined
                style={{
                  fontSize: '48px',
                  color: '#faad14',
                  marginBottom: '16px',
                }}
              />
              <Title level={4}>Componentes</Title>
              <Text style={{ fontSize: '18px' }}>Layout + Menu + Header</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card className='openManus-card openManus-shadow'>
            <div style={{ textAlign: 'center' }}>
              <HeartOutlined
                style={{
                  fontSize: '48px',
                  color: '#ff4d4f',
                  marginBottom: '16px',
                }}
              />
              <Title level={4}>Customização</Title>
              <Text style={{ fontSize: '18px' }}>Cores + Fontes + Estilos</Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Tabs com exemplos */}
      <Card className='openManus-card openManus-shadow-lg'>
        <Tabs items={tabItems} defaultActiveKey='1' />
      </Card>

      {/* Informações do tema */}
      <Card
        title='Informações do Tema'
        className='openManus-card openManus-shadow'
        style={{ marginTop: '32px' }}
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Title level={5}>🎨 Características do Tema:</Title>
            <ul>
              <li>✅ Cores primárias customizadas</li>
              <li>✅ Tipografia otimizada (System fonts)</li>
              <li>✅ Componentes com bordas arredondadas</li>
              <li>✅ Sombras e efeitos modernos</li>
              <li>✅ Suporte a tema escuro</li>
              <li>✅ Variáveis CSS globais</li>
            </ul>
          </Col>
          <Col xs={24} md={12}>
            <Title level={5}>🛠️ Tecnologias:</Title>
            <ul>
              <li>🔷 Ant Design ConfigProvider</li>
              <li>🔷 ThemeProvider customizado</li>
              <li>🔷 CSS Variables</li>
              <li>🔷 React Context para estado do tema</li>
              <li>🔷 LocalStorage para persistência</li>
              <li>🔷 Media Query para detecção automática</li>
            </ul>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default ThemeDemoPage;
