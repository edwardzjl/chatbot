import "./index.css";

import { useCallback, useContext, useEffect, useState } from "react";
import { Outlet, redirect, useNavigate } from "react-router-dom";

import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

import { SnackbarContext } from "@/contexts/snackbar";
import { ThemeContext } from "@/contexts/theme";
import { ConversationContext } from "@/contexts/conversation";
import { MessageContext } from "@/contexts/message";
import { WebsocketContext } from "@/contexts/websocket";

import Sidebar from "./Sidebar";
import ShareConvDialog from "./ShareConvDialog";
import ConvSharedDialog from "./ConvSharedDialog";
import DeleteConvDialog from "./DeleteConvDialog";

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

    const { theme } = useContext(ThemeContext);
    const { snackbar, setSnackbar } = useContext(SnackbarContext);
    const { dispatch } = useContext(MessageContext);
    const { registerMessageHandler, unregisterMessageHandler } = useContext(WebsocketContext);

    const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
    const [isSharedDialogOpen, setIsSharedDialogOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    // A transient state to store the target conversation to be shared or deleted
    const [targetConv, setTargetConv] = useState({});

    const navigate = useNavigate();

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

    const onShareClick = (id, title) => {
        setTargetConv({ id, title });
        setIsShareDialogOpen(true);
    };

    const onDeleteClick = (id, title) => {
        setTargetConv({ id, title });
        setIsDeleteDialogOpen(true);
    };

    const deleteConv = async (id) => {
        await fetch(`/api/conversations/${id}`, { method: "DELETE" });
        dispatchConv({ type: "deleted", convId: id });
        setIsDeleteDialogOpen(false);
        setTargetConv({});
        navigate("/");
    };

    const shareConv = async (id, title) => {
        const response = await fetch(`/api/shares`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: title, source_id: id }),
        });
        if (response.ok) {
            const data = await response.json();
            setTargetConv({ title: data.title, url: data.url });
            setIsShareDialogOpen(false);
            setIsSharedDialogOpen(true);
        } else {
            setSnackbar({
                open: true,
                severity: "error",
                message: "Failed to share conversation",
            });
        }
    };

    const closeSnackbar = (event, reason) => {
        if (reason === "clickaway") {
            return;
        }
        setSnackbar({ ...snackbar, open: false });
    };

    return (
        <div className={`App theme-${theme}`}>
            <Sidebar onShareClick={onShareClick} onDeleteClick={onDeleteClick} />
            <Outlet />
            <ShareConvDialog
                isOpen={isShareDialogOpen}
                onClose={() => setIsShareDialogOpen(false)}
                targetConv={targetConv}
                onShare={shareConv}
            />
            <ConvSharedDialog
                isOpen={isSharedDialogOpen}
                onClose={() => setIsSharedDialogOpen(false)}
                targetConv={targetConv}
            />
            <DeleteConvDialog
                isOpen={isDeleteDialogOpen}
                onClose={() => setIsDeleteDialogOpen(false)}
                targetConv={targetConv}
                onDelete={deleteConv}
            />
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
