import "./index.css";

import { useContext, useEffect, useRef, useState } from "react";
import { Outlet, redirect, useNavigate } from "react-router-dom";

import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";
import Tooltip from "@mui/material/Tooltip";

import ContentCopyIcon from "@mui/icons-material/ContentCopy";

import { SnackbarContext } from "@/contexts/snackbar";
import { ThemeContext } from "@/contexts/theme";
import { ConversationContext } from "@/contexts/conversation";
import { MessageContext } from "@/contexts/message";
import { WebsocketContext } from "@/contexts/websocket";

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

    const { theme } = useContext(ThemeContext);
    const { snackbar, setSnackbar } = useContext(SnackbarContext);
    const { dispatch } = useContext(MessageContext);
    const { data } = useContext(WebsocketContext);

    const shareDialogRef = useRef();
    const sharedDialogRef = useRef();
    const delDialogRef = useRef();
    // A transient state to store the target conversation to be shared or deleted
    const [targetConv, setTargetConv] = useState({});
    const [copyTooltipTitle, setCopyTooltipTitle] = useState("copy url");

    const navigate = useNavigate();

    useEffect(() => {
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
                    message: message,
                });
                break;
            case "AIMessageChunk":
                dispatch({
                    type: "appended",
                    message: message,
                });
                break;
            case "info":
                if (message.content.type === "title-generated") {
                    dispatchConv({ type: "renamed", convId: message.conversation, title: message.content.payload });
                } else {
                    console.log("unhandled info message", message);
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
    }, [data, dispatch, dispatchConv, setSnackbar]);

    const onShareClick = (id, title) => {
        setTargetConv({ id, title });
        shareDialogRef.current?.showModal();
    };

    const onCopyClick = (content) => {
        navigator.clipboard.writeText(content);
        setCopyTooltipTitle("copied!");
        setTimeout(() => {
            setCopyTooltipTitle("copy url");
        }, 3000);
    };

    const onDeleteClick = (id, title) => {
        setTargetConv({ id, title });
        delDialogRef.current?.showModal();
    };

    const deleteConv = async (id) => {
        delDialogRef.current?.close();
        setTargetConv({});
        await fetch(`/api/conversations/${id}`, { method: "DELETE" });
        dispatchConv({ type: "deleted", convId: id });
        navigate("/");
    };

    const shareConv = async (id, title) => {
        const response = await fetch(`/api/shares`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: title, source_id: id }),
        });
        shareDialogRef.current?.close();
        if (response.ok) {
            const data = await response.json();
            setTargetConv({ title: data.title, url: data.url });
            sharedDialogRef.current?.showModal();
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
            <dialog
                id="share-conv-dialog"
                className="del-dialog"
                ref={shareDialogRef}
            >
                <h2>Share conversation</h2>
                <div className="del-dialog-content">
                    <label>title:</label>
                    <input id="title" type="text" defaultValue={targetConv.title || ""} />
                </div>
                <div className="del-dialog-actions">
                    <button autoFocus onClick={() => shareConv(targetConv.id, targetConv.title)}>Ok</button>
                    <button onClick={() => shareDialogRef.current?.close()}>Cancel</button>
                </div>
            </dialog>
            <dialog
                id="conv-shared-dialog"
                className="del-dialog"
                ref={sharedDialogRef}
            >
                <h2>Conversation shared</h2>
                <div className="del-dialog-content">
                    <input id="shared-url" type="url" readOnly value={targetConv.url || ""} />
                    {/* Set slotProps or the tooltip won't be visible */}
                    {/* See <https://github.com/mui/material-ui/issues/40870#issuecomment-2044719356> */}
                    <Tooltip title={copyTooltipTitle} slotProps={{ popper: { disablePortal: true } }} >
                        <ContentCopyIcon onClick={() => onCopyClick(targetConv.url)} />
                    </Tooltip>
                </div>
                <div className="del-dialog-actions">
                    <button onClick={() => sharedDialogRef.current?.close()}>Ok</button>
                </div>
            </dialog>
            <dialog
                id="del-conv-dialog"
                className="del-dialog"
                ref={delDialogRef}
            >
                <h2>Delete conversation?</h2>
                <div className="del-dialog-content">
                    <p>This will delete &quot;{targetConv.title}&quot;</p>
                </div>
                <div className="del-dialog-actions">
                    <button autoFocus onClick={() => deleteConv(targetConv.id)}>Delete</button>
                    <button onClick={() => delDialogRef.current?.close()}>Cancel</button>
                </div>
            </dialog>
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
