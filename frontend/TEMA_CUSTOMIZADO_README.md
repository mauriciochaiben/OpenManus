# 🎨 Sistema de Tema OpenManus

## Visão Geral

O OpenManus possui um sistema de tema customizado completo baseado no Ant Design ConfigProvider, oferecendo:

- ✅ **Tema claro e escuro** com troca dinâmica
- ✅ **Cores primárias customizadas** para identidade visual
- ✅ **Tipografia otimizada** com system fonts
- ✅ **Componentes estilizados** com bordas arredondadas e sombras
- ✅ **Variáveis CSS globais** para consistência
- ✅ **Persistência automática** da preferência do usuário

## 📁 Estrutura de Arquivos

```
frontend/src/theme/
├── theme.ts              # Configuração principal do tema
├── ThemeProvider.tsx     # Provider React para gerenciamento
├── theme.css            # Estilos CSS customizados
└── index.ts             # Exports do módulo
```

## 🎯 Configuração Principal

### `theme.ts`
Define o objeto de configuração do Ant Design com:

```typescript
const openManusTheme: ThemeConfig = {
  token: {
    // Cores primárias
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',

    // Tipografia
    fontFamily: 'System fonts stack',
    fontSize: 14,

    // Layout
    borderRadius: 8,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
  },

  components: {
    // Customizações específicas por componente
    Button: { borderRadius: 8, fontWeight: 500 },
    Card: { borderRadius: 12 },
    Menu: { itemHeight: 40 },
    // ... mais componentes
  }
};
```

### `ThemeProvider.tsx`
Gerencia o estado do tema com:

- 🔄 **Troca dinâmica** entre claro/escuro
- 💾 **Persistência** no localStorage
- 🎯 **Detecção automática** da preferência do sistema
- 🎨 **Aplicação** de variáveis CSS

## 🚀 Como Usar

### 1. Importar o ThemeProvider

```typescript
// main.tsx
import { ThemeProvider } from './theme';
import ptBR from 'antd/locale/pt_BR';

<ThemeProvider locale={ptBR}>
  <App />
</ThemeProvider>
```

### 2. Usar o Hook useTheme

```typescript
// Qualquer componente
import { useTheme } from '../theme';

const MyComponent = () => {
  const { isDarkMode, toggleTheme, currentTheme } = useTheme();

  return (
    <Button onClick={toggleTheme}>
      {isDarkMode ? '☀️ Claro' : '🌙 Escuro'}
    </Button>
  );
};
```

### 3. Aplicar Classes CSS Customizadas

```tsx
// Usar classes utilitárias
<Card className="openManus-card openManus-shadow">
  <Button className="openManus-btn-primary">
    Botão Customizado
  </Button>
</Card>
```

## 🎨 Cores do Tema

### Cores Primárias
- **Primary**: `#1890ff` - Azul principal
- **Success**: `#52c41a` - Verde para sucesso
- **Warning**: `#faad14` - Laranja para avisos
- **Error**: `#ff4d4f` - Vermelho para erros

### Tema Claro
- **Background**: `#f5f5f5`
- **Container**: `#ffffff`
- **Text**: `#262626`
- **Border**: `#d9d9d9`

### Tema Escuro
- **Background**: `#000000`
- **Container**: `#141414`
- **Text**: `#ffffff`
- **Border**: `#434343`

## 🔧 Variáveis CSS Disponíveis

```css
:root {
  /* Cores */
  --color-primary: #1890ff;
  --color-success: #52c41a;
  --color-warning: #faad14;
  --color-error: #ff4d4f;

  /* Espaçamentos */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Bordas */
  --border-radius-sm: 6px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;

  /* Sombras */
  --box-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
  --box-shadow-md: 0 2px 8px rgba(0, 0, 0, 0.15);
  --box-shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

## 📱 Classes Utilitárias

### Layout
- `.openManus-card` - Card com estilo customizado
- `.openManus-shadow` - Sombra padrão
- `.openManus-shadow-lg` - Sombra grande
- `.openManus-rounded` - Bordas arredondadas
- `.openManus-rounded-lg` - Bordas arredondadas grandes

### Espaçamento
- `.openManus-mb-sm/md/lg` - Margin bottom
- `.openManus-mt-sm/md/lg` - Margin top
- `.openManus-p-sm/md/lg` - Padding

### Animações
- `.openManus-fade-in` - Fade in simples
- `.openManus-fade-in-up` - Fade in com movimento para cima

### Texto
- `.openManus-text-center` - Texto centralizado
- `.openManus-text-right` - Texto à direita

## 🎯 Componentes Customizados

### Botões
```tsx
<Button type="primary" className="openManus-btn-primary">
  Botão Primary Customizado
</Button>
```

### Inputs
```tsx
<Input placeholder="Input customizado" className="openManus-input" />
```

### Menu (no MainLayout)
```tsx
<Menu className="openManus-menu" theme="dark">
  {/* Menu items */}
</Menu>
```

## 🔄 Troca de Tema

### Automática
O tema detecta automaticamente a preferência do sistema:

```typescript
// Detecta se o usuário prefere tema escuro
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
```

### Manual
O usuário pode trocar manualmente:

```typescript
const { toggleTheme } = useTheme();

// Alterna entre claro e escuro
toggleTheme();
```

### Persistência
A preferência é salva automaticamente:

```typescript
// Salva no localStorage
localStorage.setItem('openManus-theme', 'dark');
```

## 📱 Responsividade

O tema inclui breakpoints responsivos:

```css
/* Mobile */
@media (max-width: 576px) {
  .openManus-layout .ant-layout-content {
    padding: 16px;
  }
}

/* Tablet */
@media (max-width: 768px) {
  .openManus-layout .ant-layout-sider {
    transform: translateX(-100%);
  }
}
```

## 🎨 Customização Avançada

### Adicionar Novas Cores
```typescript
// theme.ts
const customTheme = {
  ...openManusTheme,
  token: {
    ...openManusTheme.token,
    colorCustom: '#purple',
  }
};
```

### Customizar Componentes
```typescript
// theme.ts
components: {
  Button: {
    borderRadius: 16, // Bordas mais arredondadas
    controlHeight: 44, // Altura maior
  }
}
```

### Adicionar Variáveis CSS
```css
/* theme.css */
:root {
  --my-custom-color: #123456;
  --my-custom-spacing: 20px;
}
```

## 🧪 Página de Demonstração

Acesse `/theme-demo` para ver todos os componentes com o tema aplicado:

- ✅ Botões, inputs, selects
- ✅ Cards, badges, ícones
- ✅ Tipografia completa
- ✅ Troca de tema em tempo real
- ✅ Exemplos de todas as classes CSS

## 🔍 Debug e Desenvolvimento

### Ver Tema Atual
```typescript
const { currentTheme, isDarkMode } = useTheme();
console.log('Tema atual:', currentTheme);
console.log('Modo escuro:', isDarkMode);
```

### Variáveis CSS no DevTools
Inspecione o elemento `:root` para ver todas as variáveis CSS aplicadas.

### Classes Aplicadas
O body recebe automaticamente as classes:
- `.light-theme` - Tema claro
- `.dark-theme` - Tema escuro

## 📝 Próximos Passos

1. **Temas adicionais** - Criar variações de cor
2. **Modo automático** - Alternância baseada no horário
3. **Temas por usuário** - Personalização individual
4. **Animações** - Transições suaves entre temas
5. **Acessibilidade** - Contraste e tamanhos de fonte

## 🤝 Contribuição

Para contribuir com o sistema de tema:

1. Edite `theme.ts` para configurações globais
2. Adicione estilos em `theme.css` para customizações específicas
3. Use `ThemeProvider.tsx` para lógica de estado
4. Teste na página `/theme-demo`
5. Documente mudanças neste README
