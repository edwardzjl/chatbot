import "./index.css";

import { useContext } from "react";
import Avatar from "@mui/material/Avatar";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import LogoutOutlinedIcon from "@mui/icons-material/LogoutOutlined";

import { getFirstLetters, stringToColor, getCookie } from "commons";
import { UserContext, ConversationContext } from "contexts";
import { createConversation } from "requests";
import ChatTab from "components/SideMenu/SideMenuButton";

/**
 *
 */
const SideMenu = () => {
  const username = useContext(UserContext);
  const { conversations, dispatch } = useContext(ConversationContext);

  const createChat = () => {
    createConversation().then((data) => {
      dispatch({
        type: "added",
        conversation: data,
      });
    });
  };

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
      {conversations?.map((chat, index) => (
        <ChatTab key={index} chat={chat} />
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
