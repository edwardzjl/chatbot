import "./index.css";

import { useContext } from "react";
import Avatar from "@mui/material/Avatar";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import LogoutOutlinedIcon from "@mui/icons-material/LogoutOutlined";

import { getFirstLetters, stringToColor, getCookie } from "commons";
import { ConversationContext, conversationsReducer } from "contexts/conversation";
import { UserContext } from "contexts/user";
import { createConversation, getConversation } from "requests";
import ChatTab from "components/SideMenu/SideMenuButton";

/**
 *
 */
const SideMenu = () => {
  const { username } = useContext(UserContext);
  const { conversations, dispatch } = useContext(ConversationContext);

  const createChat = () => {
    createConversation()
      .then((data) => {
        dispatch({
          type: "added",
          conversation: data,
        });
      }).catch((error) => {
        console.error("Failed to create chat:", error);
      });
  };

  const onConvDeleted = (conv) => {
    const deleteAction = {
      type: "deleted",
      id: conv.id,
    };
    const nextState = conversationsReducer(conversations, deleteAction);
    if (!nextState.length) {
      createConversation()
        .then((data) => {
          dispatch({
            type: "added",
            conversation: data,
          });
        });
    } else {
      // there's still conversations left, check if we are deleting the active one
      if (conv.active) {
        // switch to the first conversation
        getConversation(nextState[0].id)
          .then((data) => {
            dispatch({
              type: "selected",
              data: data,
            });
          });
      }
    }
  }

  const handleLogout = async (e) => {
    e.preventDefault();
    const sessionId = getCookie("authservice_session");
    await fetch("/authservice/logout", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${sessionId}`,
      },
    });
    // refresh whether logout success or failure.
    window.location.reload();
  };

  return (
    <aside className="sidemenu">
      <div className="sidemenu-button" onClick={createChat}>
        <AddOutlinedIcon />
        New Chat
      </div>
      {conversations?.map((chat) => (
        <ChatTab key={chat.id} chat={chat} onConvDeleted={onConvDeleted}/>
      ))}
      <hr className="sidemenu-userinfo-hr" />
      <div className="sidemenu-userinfo">
        <Avatar
          // className not working on Avatar
          sx={{
            width: 24,
            height: 24,
            fontSize: "0.6rem",
            bgcolor: stringToColor(username),
          }}
        >
          {getFirstLetters(username)}
        </Avatar>
        <div className="sidemenu-userinfo-username">{username}</div>
        <LogoutOutlinedIcon
          className="sidemenu-userinfo-logout"
          onClick={handleLogout}
        />
      </div>
    </aside>
  );
};

export default SideMenu;
