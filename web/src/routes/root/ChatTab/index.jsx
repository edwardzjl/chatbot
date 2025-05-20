import styles from "./index.module.css";

import { useContext, useEffect, useState, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import PropTypes from "prop-types";
import Tooltip from "@mui/material/Tooltip";
import Icon from "@mui/material/Icon";

import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import DriveFileRenameOutlineIcon from "@mui/icons-material/DriveFileRenameOutline";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import ShareIcon from '@mui/icons-material/Share';

import { Dropdown, DropdownButton, DropdownMenu } from "@/components/DropdownMenu";
import { ConversationContext } from "@/contexts/conversation";
import { SnackbarContext } from "@/contexts/snackbar";
import { useDialog } from "@/contexts/dialog/hook";


/**
 *
 * @param {Object} chat
 * @param {string} chat.id
 * @param {string} chat.title
 * @returns
 */
const ChatTab = ({ chat }) => {
    const navigate = useNavigate();
    const params = useParams();
    const { openDialog } = useDialog();

    const { dispatch } = useContext(ConversationContext);
    const { setSnackbar } = useContext(SnackbarContext);
    const titleRef = useRef(null);
    const [titleText, setTitleText] = useState(chat.title);
    const [titleReadOnly, setTitleReadonly] = useState(true);
    const buttonRef = useRef(null);

    useEffect(() => {
        setTitleText(chat.title);
    }, [chat.title]);

    useEffect(() => {
        if (!titleReadOnly) {
            titleRef.current.focus();
        }
    }, [titleReadOnly]);

    const onTitleClick = (e) => {
        if (!titleReadOnly) {
            // Current editing
            e.stopPropagation();
        }
    };

    const handleKeyDown = async (e) => {
        // <https://developer.mozilla.org/zh-CN/docs/Web/API/Element/keydown_event>
        if (e.isComposing || e.keyCode === 229) {
            return;
        }
        if (e.key === "Enter") {
            e.preventDefault();
            try {
                await renameChat(titleText);
                setTitleReadonly(true);
            } catch (error) {
                setSnackbar({
                    open: true,
                    severity: "error",
                    message: `Error renaming conversation: ${error}`,
                });
            }
        }
    };

    const renameChat = async (title) => {
        const resp = await fetch(`/api/conversations/${chat.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title: title }),
        });
        if (!resp.ok) {
            // throw client errors
            throw new Error(`Error renaming conversation: ${resp}`);
        }
    };

    const onUpdateClick = (e) => {
        e.preventDefault();
        setTitleReadonly(false);
        setTimeout(() => titleRef.current.focus(), 100);
    };

    const onSummarizeClick = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch(`/api/conversations/${chat.id}/summarization`, { method: "POST" });
            const data = await res.json();
            setTitleReadonly(data.title);
        } catch (error) {
            setSnackbar({
                open: true,
                severity: "error",
                message: `Error generating conversation title: ${error}`,
            });
        }
    }

    const handleShareClick = () => {
        openDialog('share-conv-dialog', { convData: chat });
    };

    const handleDeleteClick = () => {
        openDialog('del-conv-dialog', { convData: chat });
    };

    const flipPin = async (e) => {
        e.preventDefault();
        const resp = await fetch(`/api/conversations/${chat.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                pinned: !chat.pinned,
            }),
        });
        if (!resp.ok) {
            console.error("error updating conversation", resp);
            // TODO: handle error
            // Maybe set snackbar to inform user?
        }
        dispatch({
            type: "reordered",
            conv: { ...chat, pinned: !chat.pinned },
        })
    };

    return (
        <div
            className={`${styles.sidebarButton} ${params.convId === chat.id ? styles.active : ""}`}
        >
            <Tooltip title={titleText} placement="right-start">
                <div
                    className={styles.titleContainer}
                    onClick={() => navigate(`/conversations/${chat.id}`)}
                >
                    <input
                        aria-label="chat title"
                        ref={titleRef}
                        className={styles.chatTitle}
                        readOnly={titleReadOnly}
                        onKeyDown={handleKeyDown}
                        onBlur={() => { setTitleReadonly(true); setTitleText(chat.title) }} // reset title on blur
                        onClick={onTitleClick}
                        value={titleText}
                        onChange={(e) => setTitleText(e.target.value)}
                    />
                </div>
            </Tooltip>
            <Dropdown className={styles.chatOpMenu}>
                <DropdownButton ref={buttonRef} className={styles.chatOpMenuIcon}>
                    <MoreVertIcon />
                </DropdownButton>
                <DropdownMenu buttonRef={buttonRef} className={styles.chatOpMenuList}>
                    <li>
                        <button className={styles.chatOpMenuItem} onClick={flipPin}>
                            {chat.pinned ?
                                <>
                                    <Icon baseClassName="material-symbols-outlined">keep_off</Icon>
                                    <span className={styles.chatOpMenuItemText}>Unpin</span>
                                </> : <>
                                    <Icon baseClassName="material-symbols-outlined">keep</Icon>
                                    <span className={styles.chatOpMenuItemText}>Pin</span>
                                </>
                            }
                        </button>
                    </li>
                    <li>
                        <button className={styles.chatOpMenuItem} onClick={onSummarizeClick}>
                            <AutoAwesomeIcon />
                            <span className={styles.chatOpMenuItemText}>Generate title</span>
                        </button>
                    </li>
                    <li>
                        <button className={styles.chatOpMenuItem} onClick={onUpdateClick}>
                            <DriveFileRenameOutlineIcon />
                            <span className={styles.chatOpMenuItemText}>Change title</span>
                        </button>
                    </li>
                    <li>
                        <button className={styles.chatOpMenuItem} onClick={handleShareClick}>
                            <ShareIcon />
                            <span className={styles.chatOpMenuItemText}>Share</span>
                        </button>
                    </li>
                    <li>
                        <button className={styles.chatOpMenuItem} onClick={handleDeleteClick}>
                            <DeleteOutlineIcon />
                            <span className={styles.chatOpMenuItemText}>Delete</span>
                        </button>
                    </li>
                </DropdownMenu>
            </Dropdown>
        </div>
    );
};

ChatTab.propTypes = {
    chat: PropTypes.shape({
        id: PropTypes.string.isRequired,
        title: PropTypes.string.isRequired,
        pinned: PropTypes.bool.isRequired,
    }).isRequired,
};

export default ChatTab;
