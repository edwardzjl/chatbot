import "normalize.css";
import "./index.css";

import React from "react";
import ReactDOM from "react-dom/client";
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

import Root, { action as rootAction } from "routes/root";
import Index from "routes/index";
import Conversation, { loader as conversationLoader } from "routes/conversation";
import ErrorPage from "error-page";

import reportWebVitals from "./reportWebVitals";

import { SnackbarProvider } from "contexts/snackbar";
import { ThemeProvider } from "contexts/theme";
import { UserProvider } from "contexts/user";
import { ConversationProvider } from "contexts/conversation";
import { MessageProvider } from "contexts/message";

const router = createBrowserRouter([
  {
    path: "/",
    id: "root",
    element: <Root />,
    errorElement: <ErrorPage />,
    action: rootAction,
    children: [
      {
        errorElement: <ErrorPage />,
        children: [
          {
            index: true,
            element: <Index />,
          },
          {
            path: "conversations/:convId",
            element: <Conversation />,
            loader: conversationLoader,
            shouldRevalidate: ({ currentParams, nextParams }) => {
              // prevent revalidating when clicking on the same conversation
              return currentParams.convId !== nextParams.convId;
            }
          }
        ]
      }
    ]
  }
]);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ThemeProvider>
      <SnackbarProvider>
        <UserProvider>
          <ConversationProvider>
            <MessageProvider>
              <RouterProvider router={router} />
            </MessageProvider>
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
