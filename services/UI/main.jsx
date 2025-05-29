// services/UI/main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css';       // ← thêm tại đây
import App from './app.jsx'


ReactDOM.createRoot(
  document.getElementById('root')
).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
