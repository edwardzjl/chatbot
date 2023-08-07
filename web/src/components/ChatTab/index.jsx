import "./index.css";

import { useState, useEffect, useRef, useContext } from "react";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import ClickAwayListener from "@mui/base/ClickAwayListener";

import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import DriveFileRenameOutlineIcon from "@mui/icons-material/DriveFileRenameOutline";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseOutlinedIcon from "@mui/icons-material/CloseOutlined";
import { ConversationContext, SnackbarContext } from "contexts";
import { conversationsReducer } from "conversationsReducer";
import {
  createConversation,
  deleteConversation,
  updateConversation,
} from "requests";

/**
 *
 * @param {Object} props
 * @param {number} props.key
 * @param {Object} props.chat
 * @param {string} props.chat.id
 * @param {string} props.chat.title
 * @param {boolean} props.chat.selected whether this chat is selected
 * @returns
 */
const ChatTab = (props) => {
  const { conversations, dispatch } = useContext(ConversationContext);
  const setSnackbar = useContext(SnackbarContext);

  const [title, setTitle] = useState(props.chat?.title);
  useEffect(() => {
    setTitle(props.chat?.title);
  }, [props.chat?.title]);
  const titleRef = useRef(null);

  const [operationConfirm, setOperationConfirm] = useState(
    /** @type {[{onConfirm: boolean, operation: string}]} */ {
      onConfirm: false,
    }
  );

  const handleTitleChange = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setTitle(() => e.target.value);
  };

  const onTitleFocus = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setOperationConfirm({ onConfirm: true, operation: "rename" });
  };

  const selectChat = async (e, chatId) => {
    e.preventDefault();
    e.stopPropagation();
    dispatch({
      type: "selected",
      id: chatId,
    });
  };

  const deleteChat = async (chatId) => {
    deleteConversation(chatId)
      .then(() => {
        const action = {
          type: "deleted",
          id: chatId,
        };
        dispatch(action);
        const nextState = conversationsReducer(conversations, action);
        if (!nextState.length) {
          createConversation().then((data) => {
            dispatch({
              type: "added",
              conversation: data,
            });
          });
        }
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

  const renameChat = async (id, title) => {
    updateConversation(id, title).then((res) => {
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

  const renameConfirmation = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    titleRef.current.focus();
    setOperationConfirm({ onConfirm: true, operation: "rename" });
  };

  const deleteConfirmation = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setOperationConfirm({ onConfirm: true, operation: "delete" });
  };

  const onConfirm = async (e, chatId) => {
    e.preventDefault();
    e.stopPropagation();
    if (operationConfirm.operation === "delete") {
      deleteChat(chatId);
    } else if (operationConfirm.operation === "rename") {
      renameChat(chatId, title);
    }
    setOperationConfirm({ onConfirm: false });
  };

  const onCancel = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setOperationConfirm({ onConfirm: false });
  };

  return (
    <div
      className={`sidemenu-button ${props.chat.active && "selected"}`}
      onClick={(e) => selectChat(e, props.chat.id)}
    >
      <Tooltip title={title}>
        <TextField
          id="chat-title"
          inputRef={titleRef}
          variant="standard"
          value={title}
          onChange={(e) => handleTitleChange(e)}
          onFocus={(e) => onTitleFocus(e)}
          InputProps={{ disableUnderline: true }}
          sx={{
            maxWidth: 140,
            input: {
              height: 10,
              color: "common.white",
            },
          }}
        />
      </Tooltip>

      <div className="sidemenu-button-operations">
        {/* Operations */}
        {!operationConfirm?.onConfirm && (
          <div>
            <DriveFileRenameOutlineIcon
              onClick={(e) => renameConfirmation(e)}
            />
            <DeleteOutlineIcon onClick={(e) => deleteConfirmation(e)} />
          </div>
        )}
        {/* Confirmations */}
        {operationConfirm?.onConfirm && (
          <ClickAwayListener onClickAway={onCancel}>
            <div>
              <CheckOutlinedIcon onClick={(e) => onConfirm(e, props.chat.id)} />
              <CloseOutlinedIcon onClick={(e) => onCancel(e)} />
            </div>
          </ClickAwayListener>
        )}
      </div>
    </div>
  );
};

export default ChatTab;
