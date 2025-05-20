import "./index.css";

import { useCallback, useContext, useEffect } from "react";
import { Outlet, redirect } from "react-router-dom";

import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

import { useSnackbar } from "@/contexts/snackbar/hook";
import { useTheme } from "@/contexts/theme/hook";
import { ConversationContext } from "@/contexts/conversation";
import { MessageContext } from "@/contexts/message";
import { useWebsocket } from "@/contexts/websocket/hook";

import ShareConvDialog from "@/components/dialogs/ShareConvDialog";
import ConvSharedDialog from "@/components/dialogs/ConvSharedDialog";
import DeleteConvDialog from "@/components/dialogs/DeleteConvDialog";

import Sidebar from "./Sidebar";


const Alert = (props, ref) => {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
};


async function action({ request }) {
    if (request.method === "POST") {
        const conversation = await request.json();
        return redirect(`/conversations/${conversation.id}`);
    }
}

const Root = () => {
    const { dispatch: dispatchConv } = useContext(ConversationContext);

    const { theme } = useTheme();
    const { snackbar, setSnackbar, closeSnackbar  } = useSnackbar();
    const { dispatch } = useContext(MessageContext);
    const { registerMessageHandler, unregisterMessageHandler } = useWebsocket();

    const handleWebSocketMessage = useCallback((data) => {
        if (data === null || data === undefined) {
            return;
        }
        try {
            const message = JSON.parse(data);
            switch (message.type) {
            case "human":
            case "ai":
                dispatch({
                    type: "added",
                    convId: message.conversation,
                    message: message,
                });
                break;
            case "AIMessageChunk":
                dispatch({
                    type: "appended",
                    convId: message.conversation,
                    message: message,
                });
                break;
            case "info":
                if (message.content.type === "title-generated") {
                    dispatchConv({ type: "renamed", convId: message.conversation, title: message.content.payload });
                } else {
                    console.debug("unhandled info message", message);
                }
                break;
            case "error":
                setSnackbar({
                    open: true,
                    severity: "error",
                    message: "Something goes wrong, please try again later.",
                });
                break;
            default:
                console.warn("unknown message type", message.type);
            }
        } catch (error) {
            console.error("Unhandled error: Payload may not be a valid JSON.", { Data: data, errorDetails: error });
        }
    }, [dispatch, dispatchConv, setSnackbar]);

    useEffect(() => {
        // Register the message handler when component mounts
        registerMessageHandler(handleWebSocketMessage);

        // Unregister when component unmounts
        return () => {
            unregisterMessageHandler(handleWebSocketMessage);
        };
    }, [registerMessageHandler, unregisterMessageHandler, handleWebSocketMessage]);

    return (
        <div className={`App theme-${theme}`}>
            <Sidebar />
            <Outlet />
            <ShareConvDialog id="share-conv-dialog" />
            <ConvSharedDialog id="conv-shared-dialog" />
            <DeleteConvDialog id="del-conv-dialog" />
            <Snackbar
                open={snackbar.open}
                autoHideDuration={3000}
                onClose={closeSnackbar}
            >
                <Alert
                    severity={snackbar.severity}
                    sx={{ width: "100%" }}
                    onClose={closeSnackbar}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </div>
    );
}

export default Root;
Root.action = action;
