# MainLayout Refatorado - OpenManus

## Visão Geral

O `MainLayout.tsx` foi refatorado para fornecer uma estrutura de layout completa e moderna usando Ant Design, incluindo:

- **Sider**: Navegação lateral com menu organizado por grupos
- **Header**: Cabeçalho com informações do usuário e notificações
- **Content**: Área principal de conteúdo responsiva

## Características Principais

### 🎯 **Sider com Menu Organizado**
- **Principal**: Home, Dashboard
- **Funcionalidades**: Chat/Agente, Conhecimento, Workflows
- **Configurações**: LLM Config, MCP Config, Settings

### 🎨 **Header Moderno**
- Título dinâmico baseado na rota atual
- Menu dropdown do usuário com avatar
- Sistema de notificações com badge
- Design responsivo e acessível

### 📱 **Layout Responsivo**
- Sidebar fixa com 250px de largura
- Content area com padding e scroll automático
- Suporte a diferentes tamanhos de tela

## Como Usar

### Opção 1: Substituir o AppRouter atual

```tsx
// src/App.tsx ou src/main.tsx
import { MainLayout } from './layouts';
import AppRoutes from './routes';

function App() {
  return (
    <BrowserRouter>
      <NotificationProvider>
        <MainLayout>
          <AppRoutes />
        </MainLayout>
      </NotificationProvider>
    </BrowserRouter>
  );
}
```

### Opção 2: Usar em rotas específicas

```tsx
// src/routes/index.tsx
import { Route } from 'react-router-dom';
import { MainLayout } from '../layouts';
import Dashboard from '../pages/Dashboard';

<Route path="/dashboard" element={
  <MainLayout>
    <Dashboard />
  </MainLayout>
} />
```

### Opção 3: Como wrapper de layout

```tsx
// src/components/PageWrapper.tsx
import { MainLayout } from '../layouts';

const PageWrapper = ({ children }) => (
  <MainLayout>{children}</MainLayout>
);
```

## Componentes Integrados

### Menu de Navegação
```tsx
const menuItems = [
  {
    key: 'features',
    type: 'group',
    label: 'Funcionalidades',
    children: [
      { key: '/chat', icon: <MessageOutlined />, label: 'Chat/Agente' },
      { key: '/knowledge', icon: <BookOutlined />, label: 'Conhecimento' },
      { key: '/workflow', icon: <BranchesOutlined />, label: 'Workflows' }
    ]
  }
];
```

### Header do Usuário
```tsx
const userMenuItems = [
  { key: 'profile', icon: <ProfileOutlined />, label: 'Perfil' },
  { key: 'settings', icon: <SettingOutlined />, label: 'Configurações' },
  { type: 'divider' },
  { key: 'logout', icon: <LogoutOutlined />, label: 'Sair' }
];
```

## Customização

### Alterar largura do Sider
```tsx
<Sider width={300}> // Padrão: 250px
```

### Personalizar tema
```tsx
<Menu theme="light"> // Padrão: "dark"
```

### Adicionar novos itens de menu
```tsx
const menuItems = [
  // ...itens existentes
  {
    key: 'analytics',
    type: 'group',
    label: 'Analytics',
    children: [
      { key: '/reports', icon: <BarChartOutlined />, label: 'Relatórios' }
    ]
  }
];
```

## Integração com Sistema Existente

O MainLayout mantém compatibilidade com:
- ✅ Sistema de roteamento existente (React Router)
- ✅ Context providers (NotificationProvider)
- ✅ Componentes de lazy loading
- ✅ Sistema de breadcrumbs dinâmicos
- ✅ Gerenciamento de estado global

## Arquivos Relacionados

- `src/layouts/MainLayout.tsx` - Componente principal
- `src/layouts/index.ts` - Exports dos layouts
- `src/AppRouterWithMainLayout.tsx` - Exemplo de uso
- `src/pages/ExampleDashboardPage.tsx` - Página de exemplo

## Migração do Sistema Atual

Para migrar do `AppRouter.tsx` atual para o `MainLayout`:

1. **Backup**: Faça backup do `AppRouter.tsx` atual
2. **Substitua**: Use `AppRouterWithMainLayout.tsx` como base
3. **Teste**: Verifique se todas as rotas funcionam corretamente
4. **Ajuste**: Customize conforme necessário

## Performance

- ✅ Lazy loading de componentes mantido
- ✅ Menu dinâmico baseado em rotas
- ✅ Renderização otimizada do header
- ✅ Sidebar fixa para melhor UX

## Próximos Passos

1. Integrar com sistema de autenticação
2. Adicionar tema escuro/claro
3. Implementar persistência de estado do menu
4. Adicionar animações de transição
5. Suporte a múltiplos idiomas
