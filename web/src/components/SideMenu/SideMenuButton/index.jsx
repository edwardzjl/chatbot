import "./index.css";

import { useState, useEffect, useRef, useContext } from "react";
import Tooltip from "@mui/material/Tooltip";

import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import DriveFileRenameOutlineIcon from "@mui/icons-material/DriveFileRenameOutline";
import MoreVertIcon from '@mui/icons-material/MoreVert';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

import { DropdownMenu, DropdownHeader, DropdownList } from "components/DropdownMenu";
import { ConversationContext } from "contexts/conversation";
import { SnackbarContext } from "contexts/snackbar";
import {
  deleteConversation,
  getConversation,
  updateConversation,
  summarizeConversation,
} from "requests";

/**
 *
 * @param {Object} chat
 * @param {string} chat.id
 * @param {string} chat.title
 * @param {boolean} chat.active whether this chat is active
 * @returns
 */
const ChatTab = ({ chat, onConvDeleted }) => {
  const { dispatch } = useContext(ConversationContext);
  const { setSnackbar } = useContext(SnackbarContext);

  const titleRef = useRef(null);
  const [titleEditable, setTitleEditable] = useState("false");

  const [delDialogOpen, setDelDialogOpen] = useState(false);
  const delDialogRef = useRef();

  useEffect(() => {
    if (delDialogOpen) {
      delDialogRef.current?.showModal();
    } else {
      delDialogRef.current?.close();
    }
  }, [delDialogOpen]);

  const selectChat = async () => {
    if (chat.active) {
      return;
    }
    // we need to update messages, as there might be unfinished messages when we last time left the chat.
    const detailedConv = await getConversation(chat.id);
    dispatch({
      type: "selected",
      data: detailedConv,
    });
  };

  const deleteChat = async () => {
    deleteConversation(chat.id)
      .then(() => {
        dispatch({
          type: "deleted",
          id: chat.id,
        });
        onConvDeleted(chat);
        setSnackbar({
          open: true,
          severity: "success",
          message: "Chat deleted",
        });
      })
      .catch((err) => {
        console.error("error deleting chat", err);
        setSnackbar({
          open: true,
          severity: "error",
          message: "Delete chat failed",
        });
      });
  };

  const handleKeyDown = async (e) => {
    // TODO: this will trigger in Chinese IME on OSX
    if (e.key === "Enter") {
      e.preventDefault();
      await renameChat(titleRef.current.innerText);
    }
  };

  const renameChat = async (title) => {
    setTitleEditable("false");
    updateConversation(chat.id, title).then((res) => {
      if (res.ok) {
        setSnackbar({
          open: true,
          severity: "success",
          message: "Update chat success",
        });
      } else {
        setSnackbar({
          open: true,
          severity: "error",
          message: "Update chat failed",
        });
      }
    });
  };

  const onUpdateClick = async (e) => {
    // TODO: if we stop propagation, the dropdown menu will not close
    // but if we don't, the chat title will be selected
    // e.stopPropagation();
    setTitleEditable("plaintext-only");
    // TODO: does not work on first click without `setTimeout`, but works on following clicks, no clue why
    // take a look at <https://github.com/microsoft/react-native-windows/issues/9292>
    // and <https://github.com/facebook/react/issues/17894>
    setTimeout(() => {
      titleRef.current.focus();
    }, 100);
  };

  const onSummarizeClick = async () => {
    summarizeConversation(chat.id)
      .then(data => {
        titleRef.current.innerText = data.title;
        dispatch({
          type: "updated",
          conversation: { ...chat, title: data.title },
        });
      });
  }

  return (
    <div
      className={`sidemenu-button ${chat.active && "selected"}`}
      onClick={selectChat}
    >
      <Tooltip title={titleRef.current?.innerText}>
        {/* contentEditable moves control out of react, so useState won't work correctly.
          * I use ref to get the value instead.
          */}
        <span
          aria-label="chat title"
          ref={titleRef}
          className="chat-title"
          contentEditable={titleEditable}
          suppressContentEditableWarning={true}  // TODO: I'm not sure whether I can ignore this warning
          onKeyDown={handleKeyDown}
        >{chat.title}</span>
      </Tooltip>
      {chat.active && (
        <DropdownMenu className="chat-op-menu">
          <DropdownHeader className="chat-op-menu-icon" >
            <MoreVertIcon />
          </DropdownHeader>
          <DropdownList className="chat-op-menu-list">
            <li>
              <button className="chat-op-menu-item" onClick={onSummarizeClick}>
                <AutoAwesomeIcon />
                <span className="chat-op-menu-item-text">Generate title</span>
              </button>
            </li>
            <li>
              <button className="chat-op-menu-item" onClick={onUpdateClick}>
                <DriveFileRenameOutlineIcon />
                <span className="chat-op-menu-item-text">Change title</span>
              </button>
            </li>
            <li>
              <button className="chat-op-menu-item" onClick={() => setDelDialogOpen(true)}>
                <DeleteOutlineIcon />
                <span className="chat-op-menu-item-text">Delete</span>
              </button>
            </li>
          </DropdownList>
        </DropdownMenu>
      )}
      <dialog
        className="del-dialog"
        ref={delDialogRef}
      >
        <h2>Delete conversation?</h2>
        <p>This will delete '{titleRef.current?.innerText}'</p>
        <div className="del-dialog-actions">
          <button autoFocus onClick={deleteChat}>Delete</button>
          <button onClick={() => setDelDialogOpen(false)}>Cancel</button>
        </div>
      </dialog>
    </div>
  );
};

export default ChatTab;
