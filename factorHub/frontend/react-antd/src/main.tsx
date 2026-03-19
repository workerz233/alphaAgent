import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import App from './App.tsx'
import './styles/global.css'

// 设置 dayjs 中文
dayjs.locale('zh-cn')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#3b82f6',
          colorSuccess: '#10b981',
          colorWarning: '#f59e0b',
          colorError: '#ef4444',
          colorInfo: '#06b6d4',
          colorBgBase: '#f0f9ff',
          colorBgContainer: '#ffffff',
          colorBgElevated: '#ffffff',
          colorBgLayout: '#e0f2fe',
          colorBorder: '#bae6fd',
          colorBorderSecondary: '#e0f2fe',
          colorText: '#0f172a',
          colorTextSecondary: '#475569',
          colorTextTertiary: '#64748b',
          colorTextQuaternary: '#94a3b8',
          borderRadius: 12,
          wireframe: false
        },
        components: {
          Layout: {
            headerBg: 'rgba(255, 255, 255, 0.95)',
            headerHeight: 64,
            headerColor: '#0f172a'
          },
          Menu: {
            itemBg: 'transparent',
            itemSelectedBg: 'rgba(59, 130, 246, 0.1)',
            itemHoverBg: 'rgba(59, 130, 246, 0.08)'
          },
          Card: {
            colorBgContainer: '#ffffff',
            colorBorderSecondary: '#bae6fd'
          }
        }
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>
)
