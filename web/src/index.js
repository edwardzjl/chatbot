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
import Sharing from "routes/sharing";
import Share, { loader as shareLoader } from "routes/share";
import ErrorPage from "routes/error";

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
      },
      // this takes gemini as reference, the sharing(s) page lies in the same level as the conversation page
      // and the share detail page is in an standalone route
      {
        path: "sharing",
        element: <Sharing />,
      },
    ]
  },
  {
    path: "/share/:shareId",
    loader: shareLoader,
    element: <Share />,
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
