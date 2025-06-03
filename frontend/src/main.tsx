import React from 'react';
import ReactDOM from 'react-dom/client';
import ptBR from 'antd/locale/pt_BR';
import { ThemeProvider } from './theme';
import App from './App.tsx';
import './index.css';

console.log('Main.tsx carregando...');

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider locale={ptBR}>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
