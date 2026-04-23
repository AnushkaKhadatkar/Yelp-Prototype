import React from 'react'
import ReactDOM from 'react-dom/client'
<<<<<<< HEAD
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
=======
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthBootstrap } from './context/AuthContext'
import { store } from './store'
import { setStore } from './storeRef'
import './index.css'

setStore(store)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <AuthBootstrap>
          <App />
        </AuthBootstrap>
      </BrowserRouter>
    </Provider>
>>>>>>> 6a0d87b982ed2764a05a3a8d85b4960a6814e0ea
  </React.StrictMode>
)
