# Guia de Organização de Features

## Estrutura Padrão de Features

Cada feature no `frontend/src/features/` deve seguir a seguinte estrutura:

```
feature-name/
├── components/          # Componentes React específicos da feature
│   ├── ComponentName.tsx
│   └── index.ts        # Re-exporta todos os componentes
├── hooks/              # Custom hooks específicos da feature
│   ├── useFeatureName.ts
│   └── index.ts        # Re-exporta todos os hooks
├── services/           # APIs e lógica de negócio
│   ├── featureApi.ts
│   └── index.ts        # Re-exporta todos os serviços
├── store/              # Estado local da feature (Zustand, etc.)
│   ├── featureStore.ts
│   └── index.ts        # Re-exporta stores
├── types/              # Interfaces e tipos TypeScript
│   ├── index.ts        # Define e exporta todos os tipos
├── utils/              # Utilitários específicos da feature
│   ├── featureUtils.ts
│   └── index.ts        # Re-exporta utilitários
└── index.ts            # Ponto de entrada principal da feature
```

## Features Existentes

### ✅ Bem Organizadas

- **agents/** - Gestão de agentes (estrutura completa)
- **canvas/** - Interface de canvas/diagramas (implementação robusta)
- **chat/** - Sistema de chat (componentes implementados)
- **dashboard/** - Painel principal (estrutura pronta)
- **knowledge/** - Gestão de conhecimento (componentes implementados, faltam
  store/utils)
- **llm-config/** - Configuração de LLMs (feature mais completa)
- **notes/** - Sistema de notas (componentes implementados)
- **tasks/** - Gestão de tarefas (estrutura pronta)
- **workflow/** - Fluxos de trabalho (componente complexo implementado)

### 📋 Status de Implementação

| Feature    | Components | Hooks | Services | Store | Types | Utils | Status    |
| ---------- | ---------- | ----- | -------- | ----- | ----- | ----- | --------- |
| agents     | ⚪         | ⚪    | ⚪       | ⚪    | ⚪    | ⚪    | Estrutura |
| canvas     | ✅         | ✅    | ✅       | ✅    | ✅    | ✅    | Completo  |
| chat       | ✅         | ⚪    | ⚪       | ⚪    | ⚪    | ⚪    | Parcial   |
| dashboard  | ⚪         | ⚪    | ⚪       | ⚪    | ⚪    | ⚪    | Estrutura |
| knowledge  | ✅         | ✅    | ✅       | ❌    | ✅    | ❌    | Parcial   |
| llm-config | ✅         | ⚪    | ✅       | ⚪    | ✅    | ❌    | Avançado  |
| notes      | ✅         | ⚪    | ✅       | ⚪    | ✅    | ❌    | Parcial   |
| tasks      | ⚪         | ⚪    | ✅       | ⚪    | ⚪    | ❌    | Estrutura |
| workflow   | ✅         | ⚪    | ⚪       | ⚪    | ⚪    | ⚪    | Parcial   |

**Legenda:**

- ✅ Implementado
- ⚪ Estrutura criada (TODO)
- ❌ Diretório faltando

## Scripts de Reorganização

### 1. Script Genérico - `reorganize_feature.sh`

Uso:

```bash
cd frontend/src/features
./reorganize_feature.sh [nome_da_feature]
```

Este script:

- Cria a estrutura de diretórios padrão
- Move arquivos existentes para os diretórios apropriados
- Cria arquivos `index.ts` para re-exportação
- Usa `git mv` para preservar histórico

### 2. Completar Feature Knowledge

```bash
cd frontend/src/features
./reorganize_knowledge.sh
```

## Comandos Git MV para Reorganização Manual

### Caso uma feature tenha arquivos na raiz que precisam ser organizados:

```bash
# Exemplo hipotético para reorganizar uma feature desorganizada
cd frontend/src/features/example-feature

# Mover componentes
git mv ComponentA.tsx components/
git mv ComponentB.tsx components/

# Mover hooks
git mv useExampleHook.ts hooks/

# Mover serviços
git mv exampleApi.ts services/
git mv ExampleService.ts services/

# Mover stores
git mv exampleStore.ts store/

# Mover tipos
git mv exampleTypes.ts types/

# Mover utilitários
git mv exampleUtils.ts utils/
git mv helpers.ts utils/
```

## Padrões de Nomenclatura

### Componentes

- `PascalCase` para nomes de componentes
- Sufixo descritivo quando apropriado
- Exemplo: `UserProfile.tsx`, `MessageList.tsx`

### Hooks

- Prefixo `use` obrigatório
- `camelCase` para o resto do nome
- Exemplo: `useUserData.ts`, `useWebSocket.ts`

### Serviços

- Sufixo `Api` ou `Service`
- `camelCase`
- Exemplo: `userApi.ts`, `authService.ts`

### Stores

- Sufixo `Store`
- `camelCase`
- Exemplo: `userStore.ts`, `appStore.ts`

### Types

- Interfaces em `PascalCase`
- Types em `PascalCase`
- Enums em `PascalCase`

### Utils

- Funções em `camelCase`
- Constantes em `UPPER_CASE`
- Exemplo: `formatDate.ts`, `validation.ts`

## Arquivo Index.ts Principal

Cada feature deve ter um `index.ts` que re-exporta tudo:

```typescript
// feature/index.ts
export * from "./components";
export * from "./hooks";
export * from "./services";
export * from "./store";
export * from "./types";
export * from "./utils";
```

## Boas Práticas

1. **Imports relativos**: Use imports relativos dentro da feature
2. **Barrel exports**: Sempre use arquivos `index.ts` para re-exportação
3. **Separação de responsabilidades**: Mantenha cada diretório focado em sua
   responsabilidade
4. **Testes co-localizados**: Considere adicionar `__tests__/` em cada feature
5. **Documentação**: Adicione README.md para features complexas

## Validação da Estrutura

Execute o script de validação para verificar se todas as features estão bem
organizadas:

```bash
cd frontend/src/features
./validate_features_structure.sh
```

## Próximos Passos

1. **Completar feature knowledge** - Adicionar store e utils faltantes
2. **Implementar features vazias** - Priorizar agents, dashboard, tasks
3. **Adicionar testes** - Criar estrutura de testes para cada feature
4. **Documentação específica** - README para features complexas
5. **CI/CD** - Adicionar validação automática da estrutura
