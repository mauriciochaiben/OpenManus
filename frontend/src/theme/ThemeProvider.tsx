import React, { createContext, useContext, useState, useEffect } from 'react';
import { ConfigProvider, theme as antdTheme } from 'antd';
import { openManusTheme, darkTheme } from '../theme';
import type { ThemeConfig } from 'antd';

interface ThemeContextType {
    isDarkMode: boolean;
    toggleTheme: () => void;
    currentTheme: ThemeConfig;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

interface ThemeProviderProps {
    children: React.ReactNode;
    locale?: any;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children, locale }) => {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        // Recupera preferência salva ou detecta preferência do sistema
        const saved = localStorage.getItem('openManus-theme');
        if (saved) {
            return saved === 'dark';
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    });

    // Aplica o algoritmo de tema escuro quando necessário
    const currentTheme: ThemeConfig = {
        ...(isDarkMode ? darkTheme : openManusTheme),
        algorithm: isDarkMode ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
    };

    const toggleTheme = () => {
        setIsDarkMode(prev => {
            const newMode = !prev;
            localStorage.setItem('openManus-theme', newMode ? 'dark' : 'light');
            return newMode;
        });
    };

    // Aplica classes CSS no body para tema escuro
    useEffect(() => {
        document.body.className = isDarkMode ? 'dark-theme' : 'light-theme';

        // Aplica variáveis CSS customizadas
        const root = document.documentElement;
        if (isDarkMode) {
            root.style.setProperty('--ant-color-bg-container', '#141414');
            root.style.setProperty('--ant-color-bg-layout', '#000000');
            root.style.setProperty('--ant-color-text', '#ffffff');
        } else {
            root.style.setProperty('--ant-color-bg-container', '#ffffff');
            root.style.setProperty('--ant-color-bg-layout', '#f5f5f5');
            root.style.setProperty('--ant-color-text', '#262626');
        }
    }, [isDarkMode]);

    // Escuta mudanças na preferência do sistema
    useEffect(() => {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleChange = (e: MediaQueryListEvent) => {
            if (!localStorage.getItem('openManus-theme')) {
                setIsDarkMode(e.matches);
            }
        };

        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
    }, []);

    const contextValue: ThemeContextType = {
        isDarkMode,
        toggleTheme,
        currentTheme,
    };

    return (
        <ThemeContext.Provider value={contextValue}>
            <ConfigProvider
                theme={currentTheme}
                locale={locale}
            >
                {children}
            </ConfigProvider>
        </ThemeContext.Provider>
    );
};

export default ThemeProvider;
