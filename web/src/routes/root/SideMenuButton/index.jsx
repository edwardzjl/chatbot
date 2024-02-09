import "./index.css";

import { useState, useRef } from "react";
import { useFetcher } from "react-router-dom";
import Tooltip from "@mui/material/Tooltip";

import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import DriveFileRenameOutlineIcon from "@mui/icons-material/DriveFileRenameOutline";
import MoreVertIcon from '@mui/icons-material/MoreVert';
import PushPinOutlinedIcon from '@mui/icons-material/PushPinOutlined';

import { DropdownMenu, DropdownHeader, DropdownList } from "components/DropdownMenu";

/**
 *
 * @param {Object} chat
 * @param {string} chat.id
 * @param {string} chat.title
 * @param {boolean} isActive whether this chat is active
 * @returns
 */
const ChatTab = ({ chat, isActive, onDeleteClick }) => {
  const fetcher = useFetcher();

  const titleRef = useRef(null);
  const [titleEditable, setTitleEditable] = useState("false");

  const handleKeyDown = async (e) => {
    // TODO: this will trigger in Chinese IME on OSX
    if (e.key === "Enter") {
      e.preventDefault();
      await renameChat(titleRef.current.innerText);
    }
  };

  const renameChat = async (title) => {
    setTitleEditable("false");
    fetcher.submit(
      { ...chat, title: title },
      { method: "put", action: `/conversations/${chat.id}`, encType: "application/json" }
    );
    // Maybe set snackbar to inform user?
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
    fetch(`/api/conversations/${chat.id}/summarization`, {
      method: "POST",
    })
      .then(res => res.json())
      .then(data => titleRef.current.innerText = data.title);
  }

  const flipPin = () => {
    fetcher.submit(
      { ...chat, pinned: !chat.pinned },
      { method: "put", action: `/conversations/${chat.id}`, encType: "application/json" }
    );
  };

  return (
    <>
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
      {isActive && (
        <DropdownMenu className="chat-op-menu">
          <DropdownHeader className="chat-op-menu-icon" >
            <MoreVertIcon />
          </DropdownHeader>
          <DropdownList className="chat-op-menu-list">
            <li>
              <button className="chat-op-menu-item" onClick={flipPin}>
                {/* TODO: there's no 'unpin' icon in material icons for now. */}
                {/* Please see <https://github.com/google/material-design-icons/issues/1595> */}
                {chat.pinned ? <PushPinOutlinedIcon /> : <PushPinOutlinedIcon />}
                <span className="chat-op-menu-item-text">{chat.pinned ? "Unpin" : "Pin"}</span>
              </button>
            </li>
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
              <button className="chat-op-menu-item" onClick={() => onDeleteClick(chat.id, titleRef.current?.innerText)}>
                <DeleteOutlineIcon />
                <span className="chat-op-menu-item-text">Delete</span>
              </button>
            </li>
          </DropdownList>
        </DropdownMenu>
      )}
    </>
  );
};

export default ChatTab;
