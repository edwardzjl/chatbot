import "normalize.css";
import "./index.css";

import React from "react";
import ReactDOM from "react-dom/client";
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

import Root from "./routes/root";
import ErrorPage from "./error-page";

import reportWebVitals from "./reportWebVitals";

import { ConversationProvider } from "contexts/conversation";
import { SnackbarProvider } from "./contexts/snackbar";
import { ThemeProvider } from "contexts/theme";
import { UserProvider } from "contexts/user";
import { WebsocketProvider } from "contexts/websocket";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    errorElement: <ErrorPage />,
  },
]);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ThemeProvider>
      <SnackbarProvider>
        <UserProvider>
          <ConversationProvider>
            <WebsocketProvider>
              {/* <App /> */}
              <RouterProvider router={router} />
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
