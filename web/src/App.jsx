import {
    createBrowserRouter,
    RouterProvider,
} from "react-router";

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
import { UserProvider } from "@/contexts/user/provider";
import { HttpStreamProvider } from "@/contexts/httpstream/provider";


const router = createBrowserRouter([
    {
        path: "/",
        id: "root",
        element: <Root />,
        errorElement: <ErrorPage />,
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
                loader: Sharing.loader,
            },
        ]
    },
    {
        path: "/share/:shareId",
        element: <Share />,
        loader: Share.loader,
        errorElement: <ErrorPage />,
    }
]);

function App() {
    return (
        <SnackbarProvider>
            <ConfigProvider>
                <UserProvider>
                    <ConversationProvider>
                        <HttpStreamProvider>
                            <MessageProvider>
                                <DialogProvider>
                                    <RouterProvider router={router} />
                                </DialogProvider>
                            </MessageProvider>
                        </HttpStreamProvider>
                    </ConversationProvider>
                </UserProvider>
            </ConfigProvider>
        </SnackbarProvider>
    )
}

export default App
