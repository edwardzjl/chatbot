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

  const [title, setTitle] = useState(chat?.title);
  const [titleReadOnly, setTitleReadOnly] = useState(true);
  const titleRef = useRef(null);
  useEffect(() => {
    setTitle(chat?.title);
  }, [chat?.title]);
  const handleTitleChange = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setTitle(() => e.target.value);
  };

  const [delDialogOpen, setDelDialogOpen] = useState(false);
  const delDialogRef = useRef();

  useEffect(() => {
    if (delDialogOpen) {
      delDialogRef.current?.showModal();
    } else {
      delDialogRef.current?.close();
    }
  }, [delDialogOpen]);

  const selectChat = async (chat) => {
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

  const deleteChat = async (chatId) => {
    deleteConversation(chatId)
      .then(() => {
        dispatch({
          type: "deleted",
          id: chatId,
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

  const renameChat = async (e) => {
    // preventDefault prevents refresh page on form submit
    e.preventDefault();
    setTitleReadOnly(true);
    updateConversation(chat.id, title).then((res) => {
      if (res.ok) {
        setSnackbar({
          open: true,
          severity: "success",
          message: "Update chat success",
        });
      } else {
        console.error("error updating chat");
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
    console.log("onUpdateClick", titleRef);
    // e.stopPropagation();
    setTitleReadOnly(false);
    console.log("focusing")
    // TODO: does not work on first click without `setTimeout`, but works on following clicks, no clue why
    // take a look at <https://github.com/microsoft/react-native-windows/issues/9292>
    // and <https://github.com/facebook/react/issues/17894>
    setTimeout(() => {
      titleRef.current.focus();
    }, 100);
  };

  return (
    <div
      className={`sidemenu-button ${chat.active && "selected"}`}
      onClick={() => selectChat(chat)}
    >
      {/* TODO: when the title is disabled (non active chats), there's no click event on the title
        * so the user need to click in the chattab but out of chat title, which is really difficult
        */}
      <Tooltip title={title}>
        <form className="chat-title" onSubmit={(e) => renameChat(e)}>
          <input
            ref={titleRef}
            value={title}
            disabled={titleReadOnly}
            onChange={(e) => handleTitleChange(e)}
          />
        </form>
      </Tooltip>
      {chat.active && (
        <DropdownMenu className="chat-op-menu">
          <DropdownHeader className="chat-op-menu-icon" >
            <MoreVertIcon />
          </DropdownHeader>
          <DropdownList className="chat-op-menu-list">
            <li>
              <button className="chat-op-menu-item" onClick={(e) => onUpdateClick(e)}>
                <AutoAwesomeIcon />
                <span className="chat-op-menu-item-text">Generate title</span>
              </button>
            </li>
            <li>
              <button className="chat-op-menu-item" onClick={(e) => onUpdateClick(e)}>
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
        <p>This will delete '{title}'</p>
        <div className="del-dialog-actions">
          <button autoFocus onClick={() => deleteChat(chat.id)}>Delete</button>
          <button onClick={() => setDelDialogOpen(false)}>Cancel</button>
        </div>
      </dialog>
    </div>
  );
};

export default ChatTab;
