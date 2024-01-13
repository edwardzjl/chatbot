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
    element: <Root />,
    errorElement: <ErrorPage />,
    loader: rootLoader,
    action: rootAction,
    shouldRevalidate: ({ currentParams, nextParams, formMethod }) => {
      if (currentParams.convId === undefined && nextParams.convId === undefined) {
        // from index to index
        return false;
      };
      if (currentParams.convId === undefined) {
        // from index to conv
        // we need to validate this so that the newly created conv will show up.
        return true;
      };
      if (currentParams.convId === nextParams.convId) {
        // from conv to same conv
        if (formMethod === "put") {
          // revalidate on update
          // This is a bit hacky, but we need to revalidate on update so that the
          // generated conversation title will be updated.
          return true;
        }
        return false;
      };
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
            },
          },
        ],
      }
    ],
  },
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
