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

/**
 *
 * @param {Object} chat
 * @param {string} chat.id
 * @param {string} chat.title
 * @returns
 */
const ChatTab = ({ chat, onShareClick, onDeleteClick }) => {
    const navigate = useNavigate();
    const params = useParams();

    const { dispatch } = useContext(ConversationContext);
    const titleRef = useRef(null);
    const [titleEditable, setTitleEditable] = useState("false");
    const buttonRef = useRef(null);

    useEffect(() => {
        if (titleEditable === "plaintext-only") {
            titleRef.current.focus();
        }
    }, [titleEditable]);

    const handleKeyDown = async (e) => {
        // TODO: this will trigger in Chinese IME on OSX
        if (e.key === "Enter") {
            e.preventDefault();
            await renameChat(titleRef.current.innerText);
        }
    };

    const renameChat = async (title) => {
        setTitleEditable("false");
        const resp = await fetch(`/api/conversations/${chat.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                title: title,
            }),
        });
        if (!resp.ok) {
            console.error("error updating conversation", resp);
            // TODO: handle error
            // Maybe set snackbar to inform user?
        }
        titleRef.current.innerText = title;
    };
    const onUpdateClick = (e) => {
        e.preventDefault();
        setTitleEditable("plaintext-only");
        setTimeout(() => titleRef.current.focus(), 100);
    };

    const onSummarizeClick = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch(`/api/conversations/${chat.id}/summarization`, { method: "POST" });
            const data = await res.json();
            titleRef.current.innerText = data.title;
        } catch (error) {
            console.error("Error generating title", error);
            // TODO: Show snackbar or toast notification
        }
    }

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
            <Tooltip title={titleRef.current?.innerText}>
                <div
                    className={styles.titleContainer}
                    onClick={() => navigate(`/conversations/${chat.id}`)}
                >
                    {/* contentEditable moves control out of react, so useState won't work correctly.
                      * I use ref to get the value instead.
                    */}
                    <span
                        aria-label="chat title"
                        ref={titleRef}
                        className={styles.chatTitle}
                        contentEditable={titleEditable}
                        suppressContentEditableWarning={true}  // TODO: I'm not sure whether I can ignore this warning
                        onKeyDown={handleKeyDown}
                        onBlur={() => setTitleEditable("false")}
                    >
                        {chat.title}
                    </span>
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
                        <button className={styles.chatOpMenuItem} onClick={() => onShareClick(chat.id, chat.title)}>
                            <ShareIcon />
                            <span className={styles.chatOpMenuItemText}>Share</span>
                        </button>
                    </li>
                    <li>
                        <button className={styles.chatOpMenuItem} onClick={() => onDeleteClick(chat.id, titleRef.current?.innerText)}>
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
    onShareClick: PropTypes.func.isRequired,
    onDeleteClick: PropTypes.func.isRequired,
};

export default ChatTab;
