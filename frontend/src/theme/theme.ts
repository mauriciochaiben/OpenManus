import type { ThemeConfig } from 'antd';

/**
 * Tema customizado para o OpenManus
 * Define cores, tipografia e estilos de componentes para manter consistência visual
 */
const openManusTheme: ThemeConfig = {
  token: {
    // === Cores Primárias ===
    colorPrimary: '#1890ff', // Azul principal
    colorSuccess: '#52c41a', // Verde para sucesso
    colorWarning: '#faad14', // Laranja para avisos
    colorError: '#ff4d4f', // Vermelho para erros
    colorInfo: '#1890ff', // Azul para informações

    // === Cores de Fundo ===
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#f5f5f5',
    colorBgSpotlight: '#ffffff',

    // === Tipografia ===
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: 14,
    fontSizeLG: 16,
    fontSizeSM: 12,
    fontSizeXL: 20,

    // === Espaçamento ===
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 6,

    // === Layout ===
    lineHeight: 1.5714,
    lineHeightLG: 1.5,
    lineHeightSM: 1.66,

    // === Sombras ===
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
    boxShadowSecondary: '0 4px 12px rgba(0, 0, 0, 0.15)',

    // === Bordas ===
    colorBorder: '#d9d9d9',
    colorBorderSecondary: '#f0f0f0',

    // === Estados de hover/focus ===
    controlHeightLG: 40,
    controlHeight: 32,
    controlHeightSM: 24,

    // === Cores de texto ===
    colorText: '#262626',
    colorTextSecondary: '#8c8c8c',
    colorTextTertiary: '#bfbfbf',
    colorTextQuaternary: '#d9d9d9',
  },

  // === Customizações de Componentes ===
  components: {
    // Layout
    Layout: {
      bodyBg: '#f5f5f5',
      headerBg: '#ffffff',
      siderBg: '#001529',
      triggerBg: '#002140',
      triggerColor: '#ffffff',
    },

    // Menu
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: '#1890ff',
      itemSelectedColor: '#ffffff',
      itemHoverBg: 'rgba(24, 144, 255, 0.1)',
      itemHoverColor: '#1890ff',
      groupTitleColor: '#8c8c8c',
      iconSize: 16,
      itemHeight: 40,
      collapsedIconSize: 16,

      // Dark theme overrides para sidebar
      darkItemBg: 'transparent',
      darkItemSelectedBg: '#1890ff',
      darkItemSelectedColor: '#ffffff',
      darkItemHoverBg: 'rgba(255, 255, 255, 0.1)',
      darkItemHoverColor: '#ffffff',
      darkGroupTitleColor: '#8c8c8c',
    },

    // Button
    Button: {
      borderRadius: 8,
      controlHeight: 36,
      controlHeightLG: 44,
      controlHeightSM: 28,
      fontWeight: 500,
      primaryShadow: '0 2px 4px rgba(24, 144, 255, 0.2)',
    },

    // Card
    Card: {
      borderRadius: 12,
      headerBg: '#fafafa',
      headerHeight: 56,
      actionsBg: '#fafafa',
    },

    // Input
    Input: {
      borderRadius: 8,
      controlHeight: 36,
      controlHeightLG: 44,
      controlHeightSM: 28,
      paddingInline: 12,
      paddingBlock: 8,
    },

    // Select
    Select: {
      borderRadius: 8,
      controlHeight: 36,
      controlHeightLG: 44,
      controlHeightSM: 28,
    },

    // Table
    Table: {
      borderRadius: 8,
      headerBg: '#fafafa',
      headerSortActiveBg: '#f0f0f0',
      headerSortHoverBg: '#f5f5f5',
      rowHoverBg: '#f8f9fa',
    },

    // Modal
    Modal: {
      borderRadius: 12,
      contentBg: '#ffffff',
      headerBg: '#ffffff',
      footerBg: '#fafafa',
    },

    // Drawer
    Drawer: {
      borderRadius: 0,
      colorBgElevated: '#ffffff',
    },

    // Tabs
    Tabs: {
      cardBg: '#fafafa',
      itemActiveColor: '#1890ff',
      itemHoverColor: '#40a9ff',
      itemSelectedColor: '#1890ff',
      inkBarColor: '#1890ff',
      titleFontSize: 14,
    },

    // Badge
    Badge: {
      statusSize: 6,
      indicatorHeight: 20,
      indicatorHeightSM: 16,
    },

    // Avatar
    Avatar: {
      borderRadius: 8,
      groupOverlapping: -8,
      groupSpace: 4,
    },

    // Breadcrumb
    Breadcrumb: {
      fontSize: 14,
      iconFontSize: 14,
      itemColor: '#8c8c8c',
      lastItemColor: '#262626',
      linkColor: '#1890ff',
      linkHoverColor: '#40a9ff',
      separatorColor: '#bfbfbf',
    },

    // Notification
    Notification: {
      borderRadius: 8,
      padding: 16,
    },

    // Message
    Message: {
      borderRadius: 8,
      contentPadding: '10px 16px',
    },

    // Tooltip
    Tooltip: {
      borderRadius: 6,
      paddingXS: 8,
    },

    // Progress
    Progress: {
      circleTextFontSize: '1em',
      lineBorderRadius: 100,
    },

    // Spin
    Spin: {
      contentHeight: 400,
    },

    // Typography
    Typography: {
      titleMarginBottom: '0.5em',
      titleMarginTop: '1.2em',
    },
  },

  // === Configurações de algoritmo ===
  algorithm: undefined, // Pode ser configurado para tema dark: theme.darkAlgorithm
};

/**
 * Configuração de tema escuro (opcional)
 */
export const darkTheme: ThemeConfig = {
  ...openManusTheme,
  token: {
    ...openManusTheme.token,
    colorBgContainer: '#141414',
    colorBgElevated: '#1f1f1f',
    colorBgLayout: '#000000',
    colorBgSpotlight: '#262626',
    colorText: '#ffffff',
    colorTextSecondary: '#a6a6a6',
    colorTextTertiary: '#737373',
    colorTextQuaternary: '#595959',
    colorBorder: '#434343',
    colorBorderSecondary: '#303030',
  },
  components: {
    ...openManusTheme.components,
    Layout: {
      ...openManusTheme.components?.Layout,
      bodyBg: '#000000',
      headerBg: '#141414',
    },
    Card: {
      ...openManusTheme.components?.Card,
      headerBg: '#1f1f1f',
      actionsBg: '#1f1f1f',
    },
    Table: {
      ...openManusTheme.components?.Table,
      headerBg: '#1f1f1f',
    },
    Modal: {
      ...openManusTheme.components?.Modal,
      contentBg: '#1f1f1f',
      headerBg: '#1f1f1f',
      footerBg: '#141414',
    },
    Tabs: {
      ...openManusTheme.components?.Tabs,
      cardBg: '#1f1f1f',
    },
  },
};

/**
 * Variáveis CSS customizadas para uso global
 */
export const cssVariables = {
  // Cores principais
  '--color-primary': '#1890ff',
  '--color-success': '#52c41a',
  '--color-warning': '#faad14',
  '--color-error': '#ff4d4f',
  '--color-info': '#1890ff',

  // Espaçamentos
  '--spacing-xs': '4px',
  '--spacing-sm': '8px',
  '--spacing-md': '16px',
  '--spacing-lg': '24px',
  '--spacing-xl': '32px',
  '--spacing-xxl': '48px',

  // Raios de borda
  '--border-radius-sm': '6px',
  '--border-radius-md': '8px',
  '--border-radius-lg': '12px',
  '--border-radius-xl': '16px',

  // Sombras
  '--box-shadow-sm': '0 1px 3px rgba(0, 0, 0, 0.12)',
  '--box-shadow-md': '0 2px 8px rgba(0, 0, 0, 0.15)',
  '--box-shadow-lg': '0 4px 12px rgba(0, 0, 0, 0.15)',
  '--box-shadow-xl': '0 8px 24px rgba(0, 0, 0, 0.12)',

  // Tipografia
  '--font-family':
    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  '--font-size-xs': '11px',
  '--font-size-sm': '12px',
  '--font-size-md': '14px',
  '--font-size-lg': '16px',
  '--font-size-xl': '18px',
  '--font-size-xxl': '20px',

  // Line heights
  '--line-height-sm': '1.4',
  '--line-height-md': '1.5714',
  '--line-height-lg': '1.6',

  // Z-index layers
  '--z-index-dropdown': '1000',
  '--z-index-sticky': '1001',
  '--z-index-fixed': '1002',
  '--z-index-modal-backdrop': '1003',
  '--z-index-modal': '1004',
  '--z-index-popover': '1005',
  '--z-index-tooltip': '1006',
  '--z-index-notification': '1007',
};

export default openManusTheme;
