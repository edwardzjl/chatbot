import "normalize.css";
import './index.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import reportWebVitals from './reportWebVitals';

import { ConversationProvider } from "contexts/conversation";
import { SnackbarProvider } from "./contexts/snackbar";
import { ThemeProvider } from "contexts/theme";
import { UserProvider } from "contexts/user";
import { WebsocketProvider } from "contexts/websocket";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider>
      <SnackbarProvider>
        <UserProvider>
          <ConversationProvider>
            <WebsocketProvider>
              <App />
            </WebsocketProvider>
          </ConversationProvider>
        </UserProvider>
      </SnackbarProvider>
    </ThemeProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
