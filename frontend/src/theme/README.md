# OpenManus Theme System

Este diretório contém a configuração completa do sistema de temas da aplicação
OpenManus, incluindo customizações do Ant Design e estilos globais.

## Arquivos do Sistema de Tema

### `theme.ts`

Arquivo principal de configuração do tema Ant Design com a paleta de cores
OpenManus:

**Cores Principais:**

- `colorPrimary`: `#2c5aa0` (Azul OpenManus)
- `colorSuccess`: `#28a745` (Verde moderno)
- `colorWarning`: `#ffc107` (Amarelo/laranja vibrante)
- `colorError`: `#dc3545` (Vermelho moderno)
- `colorInfo`: `#17a2b8` (Azul-turquesa)

**Características:**

- Tipografia: Inter como fonte principal
- Bordas arredondadas modernas (8px padrão)
- Sombras suaves e elegantes
- Customizações específicas para componentes (Menu, Button, Card, etc.)
- Suporte para tema escuro

### `ThemeProvider.tsx`

Componente React que gerencia o contexto de tema da aplicação:

**Funcionalidades:**

- Toggle entre tema claro e escuro
- Persistência da preferência no localStorage
- ConfigProvider do Ant Design integrado
- Suporte a internacionalização (pt_BR)

### `theme.css`

Variáveis CSS globais que complementam o tema Ant Design:

**Inclui:**

- Variáveis de cor sincronizadas com o tema
- Espaçamentos padronizados
- Raios de borda consistentes
- Sombras e z-index organizados
- Configurações de tipografia

### `index.ts`

Arquivo de exportação centralizada para facilitar importações.

## Como Usar

### Usando o Tema em Componentes

```tsx
import { useTheme } from "@/theme";

function MyComponent() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <div>
      <Button onClick={toggleTheme}>
        Alternar para tema {isDark ? "claro" : "escuro"}
      </Button>
    </div>
  );
}
```

### Usando Variáveis CSS

```css
.my-component {
  background-color: var(--color-primary);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  box-shadow: var(--box-shadow-md);
}
```

### Customizando Componentes Ant Design

O tema já inclui customizações para componentes principais. Para adicionar novas
customizações:

```tsx
// No theme.ts
components: {
  MyComponent: {
    // Propriedades específicas do componente
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  }
}
```

## Paleta de Cores OpenManus

### Cores Primárias

- **Azul Principal**: `#2c5aa0` - Cor da marca OpenManus
- **Verde**: `#28a745` - Sucesso, confirmações
- **Amarelo**: `#ffc107` - Avisos, atenção
- **Vermelho**: `#dc3545` - Erros, ações destrutivas
- **Azul Info**: `#17a2b8` - Informações neutras

### Cores Secundárias

- **Fundos**: `#f8f9fa`, `#ffffff`
- **Bordas**: `#e5e7eb`, `#f3f4f6`
- **Textos**: `#1f2937`, `#6b7280`, `#9ca3af`

## Tema Escuro

O sistema inclui suporte completo a tema escuro com:

- Inversão automática de cores de fundo
- Ajuste de contraste para textos
- Manutenção da identidade visual da marca
- Transições suaves entre temas

## Extensibilidade

Para adicionar novas variáveis ou customizações:

1. **CSS Variables**: Adicione em `theme.css` e `cssVariables` em `theme.ts`
2. **Component Customizations**: Estenda o objeto `components` em `theme.ts`
3. **Dark Theme**: Adicione override específico em `darkTheme`

## Performance

O sistema de tema é otimizado para:

- Carregamento mínimo de CSS
- Alternância rápida entre temas
- Tree-shaking automático de estilos não utilizados
- Cache de preferências do usuário
