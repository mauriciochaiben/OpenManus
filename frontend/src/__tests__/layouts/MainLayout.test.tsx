import { describe, test, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import React from "react";
import MainLayout from "../../layouts/MainLayout";

// Mock mais simples do useTheme
vi.mock("../../theme", () => ({
  useTheme: () => ({
    isDarkMode: false,
    toggleTheme: vi.fn(),
    currentTheme: {},
  }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
}));

// Componente wrapper para testes
const TestWrapper: React.FC<{
  children: React.ReactNode;
  initialRoute?: string;
}> = ({ children, initialRoute = "/" }) => {
  return (
    <MemoryRouter initialEntries={[initialRoute]}>{children}</MemoryRouter>
  );
};

describe("MainLayout", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Layout Structure", () => {
    test("should render Sider, Header and Content", () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div data-testid="test-content">Test Content</div>
          </MainLayout>
        </TestWrapper>,
      );

      // Verifica se a estrutura principal está presente
      expect(screen.getByRole("banner")).toBeInTheDocument(); // Header
      expect(screen.getByTestId("test-content")).toBeInTheDocument(); // Content

      // Verifica se o logo e título estão presentes
      expect(screen.getByText("OpenManus")).toBeInTheDocument();
      expect(screen.getByText("AI Assistant Platform")).toBeInTheDocument();
    });

    test("should render logo with rocket icon", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      expect(screen.getByText("OpenManus")).toBeInTheDocument();
      expect(screen.getByText("AI Assistant Platform")).toBeInTheDocument();
    });
  });

  describe("Navigation Menu", () => {
    test("should render all main navigation groups", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // Verifica grupos do menu
      expect(screen.getByText("Principal")).toBeInTheDocument();
      expect(screen.getByText("Funcionalidades")).toBeInTheDocument();
      expect(screen.getByText("Configurações")).toBeInTheDocument();
    });

    test("should render core navigation items", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // Itens do grupo Principal
      expect(screen.getByText("Home")).toBeInTheDocument();
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });

    test("should render feature navigation items", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // Itens do grupo Funcionalidades
      expect(screen.getByText("Chat/Agente")).toBeInTheDocument();
      expect(screen.getByText("Conhecimento")).toBeInTheDocument();
      expect(screen.getByText("Workflows")).toBeInTheDocument();
      expect(screen.getByText("Canvas (Beta)")).toBeInTheDocument();
    });

    test("should render configuration navigation items", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // Itens do grupo Configurações
      expect(screen.getByText("Configurar LLM")).toBeInTheDocument();
      expect(screen.getByText("Configurar MCP")).toBeInTheDocument();
      expect(screen.getByText("Configurações")).toBeInTheDocument();
    });

    test("should have Canvas item disabled", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // O Canvas deve estar desabilitado (beta) - test via aria attributes
      const canvasItem = screen.getByText("Canvas (Beta)");
      expect(canvasItem).toBeInTheDocument();
      // Test the disabled state through aria attributes or data-testid
      expect(canvasItem).toHaveAttribute("aria-disabled", "true");
    });

    test("should highlight current route in menu", () => {
      render(
        <TestWrapper initialRoute="/chat">
          <MainLayout />
        </TestWrapper>,
      );

      // Verifica se o item atual está selecionado
      const chatItem = screen.getByText("Chat/Agente");
      expect(chatItem).toBeInTheDocument();
      // Test the selected state through aria attributes
      expect(chatItem).toHaveAttribute("aria-current", "page");
    });
  });

  describe("Header Functionality", () => {
    test("should render page title based on current route", () => {
      const testCases = [
        { route: "/", expectedTitle: "Home" },
        { route: "/dashboard", expectedTitle: "Dashboard" },
        { route: "/chat", expectedTitle: "Chat/Agente" },
        { route: "/knowledge", expectedTitle: "Base de Conhecimento" },
        { route: "/workflow", expectedTitle: "Workflows" },
        { route: "/llm-config", expectedTitle: "Configurar LLM" },
        { route: "/mcp-config", expectedTitle: "Configurar MCP" },
        { route: "/settings", expectedTitle: "Configurações" },
        { route: "/unknown", expectedTitle: "OpenManus" },
      ];

      // Test each route one by one to avoid deep nesting
      for (const { route, expectedTitle } of testCases) {
        const { unmount } = render(
          <TestWrapper initialRoute={route}>
            <MainLayout />
          </TestWrapper>,
        );

        expect(screen.getByText(expectedTitle)).toBeInTheDocument();
        unmount();
      }
    });

    test("should render theme toggle button", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // Deve haver um botão para trocar o tema
      const themeButton = screen.getByRole("button", { name: /ativar tema/i });
      expect(themeButton).toBeInTheDocument();
    });

    test("should render notifications badge", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // Deve haver uma badge de notificações
      expect(screen.getByText("3")).toBeInTheDocument(); // Badge count
    });

    test("should render user avatar and dropdown", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // Deve haver um avatar do usuário
      expect(screen.getByText("Usuário")).toBeInTheDocument();
    });
  });

  describe("User Menu", () => {
    const renderLayoutAndOpenUserMenu = async () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      const userArea = screen.getByText("Usuário");
      fireEvent.click(userArea);

      await waitFor(() => {
        expect(screen.getByText("Perfil")).toBeInTheDocument();
      });
    };

    test("should open user dropdown menu on click", async () => {
      await renderLayoutAndOpenUserMenu();
      expect(screen.getByText("Sair")).toBeInTheDocument();
    });

    test("should have logout functionality", async () => {
      const consoleSpy = vi.spyOn(console, "log").mockImplementation(() => {
        // Mock implementation
      });

      await renderLayoutAndOpenUserMenu();

      const logoutButton = screen.getByText("Sair");
      fireEvent.click(logoutButton);

      expect(consoleSpy).toHaveBeenCalledWith("Logout");
      consoleSpy.mockRestore();
    });
  });

  describe("Content Area", () => {
    test("should render children in content area", () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div data-testid="child-content">Child Content</div>
          </MainLayout>
        </TestWrapper>,
      );

      expect(screen.getByTestId("child-content")).toBeInTheDocument();
    });

    test("should render Outlet when no children provided", () => {
      // Para testar o Outlet, precisamos renderizar sem children
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // O conteúdo deve estar presente (mesmo que vazio via Outlet)
      const contentArea = screen.getByRole("main");
      expect(contentArea).toBeInTheDocument();
    });
  });

  describe("Layout Styling", () => {
    test("should have correct layout structure", () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Test</div>
          </MainLayout>
        </TestWrapper>,
      );

      // Verifica se o layout principal está configurado corretamente
      expect(screen.getByText("Test")).toBeInTheDocument();
      // Test that the layout structure is present by checking for main role
      expect(screen.getByRole("main")).toBeInTheDocument();
    });

    test("should have fixed sidebar", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // O sidebar deve estar presente
      expect(screen.getByText("OpenManus")).toBeInTheDocument();
      // Test that navigation is present
      expect(screen.getByRole("navigation")).toBeInTheDocument();
    });
  });

  describe("Responsive Behavior", () => {
    test("should maintain layout integrity", () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div data-testid="responsive-content">Responsive Test</div>
          </MainLayout>
        </TestWrapper>,
      );

      // Verifica se todos os elementos principais estão presentes
      expect(screen.getByText("OpenManus")).toBeInTheDocument(); // Logo
      expect(screen.getByText("Home")).toBeInTheDocument(); // Menu
      expect(screen.getByText("Usuário")).toBeInTheDocument(); // Header
      expect(screen.getByTestId("responsive-content")).toBeInTheDocument(); // Content
    });
  });

  describe("Accessibility", () => {
    test("should have proper semantic structure", () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Content</div>
          </MainLayout>
        </TestWrapper>,
      );

      // Verifica elementos semânticos
      expect(screen.getByRole("banner")).toBeInTheDocument(); // Header
      expect(screen.getByRole("main")).toBeInTheDocument(); // Content
      expect(screen.getByRole("navigation")).toBeInTheDocument(); // Menu
    });

    test("should have accessible buttons with titles", () => {
      render(
        <TestWrapper>
          <MainLayout />
        </TestWrapper>,
      );

      // Botão de tema deve ter título acessível
      const themeButton = screen.getByRole("button", { name: /ativar tema/i });
      expect(themeButton).toHaveAttribute("title");
    });
  });
});
