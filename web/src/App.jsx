import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import Root from "@/routes/root";
import Index from "@/routes/index";
import Conversation from "@/routes/conversation";
import Sharing from "@/routes/sharing";
import Share from "@/routes/share";
import ErrorPage from "@/routes/error";

import { SnackbarProvider } from "@/contexts/snackbar/provider";
import { ThemeProvider } from "@/contexts/theme/provider";
import { UserProvider } from "@/contexts/user/provider";
import { ConversationProvider } from "@/contexts/conversation/provider";
import { MessageProvider } from "@/contexts/message/provider";
import { WebsocketProvider } from "@/contexts/websocket/provider";


const router = createBrowserRouter([
    {
        path: "/",
        id: "root",
        element: <Root />,
        errorElement: <ErrorPage />,
        action: Root.action,
        children: [
            {
                index: true,
                element: <Index />,
            },
            {
                path: "conversations/:convId",
                element: <Conversation />,
                loader: Conversation.loader,
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
        loader: Share.loader,
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
