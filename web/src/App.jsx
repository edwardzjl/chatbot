import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import Conversation from "@/routes/conversation";
import ErrorPage from "@/routes/error";
import Index from "@/routes/index";
import Root from "@/routes/root";
import Share from "@/routes/share";
import Sharing from "@/routes/sharing";

import { ConfigProvider } from "@/contexts/config/provider";
import { ConversationProvider } from "@/contexts/conversation/provider";
import { DialogProvider } from "@/contexts/dialog/provider";
import { MessageProvider } from "@/contexts/message/provider";
import { SnackbarProvider } from "@/contexts/snackbar/provider";
import { ThemeProvider } from "@/contexts/theme/provider";
import { UserProvider } from "@/contexts/user/provider";
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
                <ConfigProvider>
                    <UserProvider>
                        <ConversationProvider>
                            <WebsocketProvider>
                                <MessageProvider>
                                    <DialogProvider>
                                        <RouterProvider router={router} />
                                    </DialogProvider>
                                </MessageProvider>
                            </WebsocketProvider>
                        </ConversationProvider>
                    </UserProvider>
                </ConfigProvider>
            </SnackbarProvider>
        </ThemeProvider>
    )
}

export default App
