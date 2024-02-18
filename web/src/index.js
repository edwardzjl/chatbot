import "normalize.css";
import "./index.css";

import React from "react";
import ReactDOM from "react-dom/client";
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

import Root, { loader as rootLoader, action as rootAction } from "routes/root";
import Index from "routes/index";
import Conversation, { loader as conversationLoader, action as conversationAction } from "routes/conversation";
import ErrorPage from "error-page";

import reportWebVitals from "./reportWebVitals";

import { SnackbarProvider } from "contexts/snackbar";
import { ThemeProvider } from "contexts/theme";
import { UserProvider } from "contexts/user";
import { MessageProvider } from "contexts/message";

const router = createBrowserRouter([
  {
    path: "/",
    id: "root",
    element: <Root />,
    errorElement: <ErrorPage />,
    loader: rootLoader,
    action: rootAction,
    shouldRevalidate: ({ currentParams, nextParams, formMethod }) => {
      // Root revalidation logic, revalidates (fetches) conversation list.
      // from index to index
      if (currentParams.convId === undefined && nextParams.convId === undefined) {
        return false;
      }
      // from index to conv
      if (currentParams.convId === undefined) {
        // Revalidate post method so that the newly created conv will show up.
        if (formMethod === "post") {
          return true;
        }
        // ignore others to prevent fetch when clicking on a conversation from index.
        return false;
      }
      // from conv to index
      if (nextParams.convId === undefined) {
        // Revalidate delete method so that the deleted conv will be removed.
        if (formMethod === "delete") {
          return true;
        }
        // ignore others to prevent fetch when clicking on index from any conversation.
        return false;
      }
      // from conv to same conv
      if (currentParams.convId === nextParams.convId) {
        // revalidate on post
        // this is a bit hacky, I trigger a 'post' action on message send for 2 reasons:
        // 1. I need to revalidate the conversations to get the 'last_message_at' updated.
        // 2. I need to revalidate the conversations when title generated.
        // 3. The 'get' method doesn't trigger actions.
        if (formMethod === "post") {
          return true;
        }
        // revalidate on put
        // I need to revalidate the conversations when conversation pinned.
        if (formMethod === "put") {
          return true;
        }
        return false;
      }
      // Ignore revalidation on conv to another conv.
      return false;
    },
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
            action: conversationAction,
            shouldRevalidate: ({ currentParams, nextParams }) => {
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
          <MessageProvider>
            <RouterProvider router={router} />
          </MessageProvider>
        </UserProvider>
      </SnackbarProvider>
    </ThemeProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
