
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'

import './App.css'

import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import Root, { action as rootAction } from "@/routes/root";
import Index from "@/routes/index";
import Conversation, { loader as conversationLoader } from "@/routes/conversation";
import Sharing from "@/routes/sharing";
import Share, { loader as shareLoader } from "@/routes/share";
import ErrorPage from "@/routes/error";

import { SnackbarProvider } from "@/contexts/snackbar/provider";
import { ThemeProvider } from "@/contexts/theme/provider";
import { UserProvider } from "@/contexts/user/provider";
import { ConversationProvider } from "@/contexts/conversation/provider";
import { MessageProvider } from "@/contexts/message/provider";
import { WebsocketProvider } from "@/contexts/websocket";


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

function App() {
    return (
        <ThemeProvider>
            <SnackbarProvider>
                <UserProvider>
                    <ConversationProvider>
                        <WebsocketProvider>
                            <MessageProvider>
                                <RouterProvider router={router} />
                            </MessageProvider>
                        </WebsocketProvider>
                    </ConversationProvider>
                </UserProvider>
            </SnackbarProvider>
        </ThemeProvider>
    )
}

export default App
