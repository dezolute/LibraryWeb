import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ConfigProvider } from 'antd'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider
      theme={{
        token: {
          // Seed Token
          colorPrimary: '#00B96B',
          borderRadius: 16,
          fontFamily: "Nunito",
          // Alias Token
          colorBgContainer: '#f6ffed',
        },
      }}
    >
      <App />
    </ConfigProvider>
  </StrictMode>,
)
