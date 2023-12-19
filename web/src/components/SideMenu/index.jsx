import "./index.css";

import { useContext, useEffect, useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import GitHubIcon from '@mui/icons-material/GitHub';
import MailOutlineIcon from '@mui/icons-material/MailOutline';

import { ConversationContext, conversationsReducer } from "contexts/conversation";
import { createConversation, getConversation } from "requests";
import ChatTab from "components/SideMenu/SideMenuButton";

/**
 *
 */
const SideMenu = () => {
  const { conversations, dispatch } = useContext(ConversationContext);
  const [groupedConvs, setGroupedConvs] = useState({});

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

  useEffect(() => {
    const groupConvs = () => {
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      const lastSevenDays = new Date(today);
      lastSevenDays.setDate(lastSevenDays.getDate() - 7);

      const _groupedConvs = Object.groupBy(conversations, (item) => {
        const itemDate = new Date(item.updated_at);
        if (itemDate.toDateString() === today.toDateString()) {
          return "Today";
        } else if (itemDate.toDateString() === yesterday.toDateString()) {
          return "Yesterday";
        } else if (itemDate > lastSevenDays) {
          return "Last seven days";
        } else {
          return `${itemDate.toLocaleString("default", { month: "long" })} ${itemDate.getFullYear()}`;
        }
      });
      setGroupedConvs(_groupedConvs);
    };
    groupConvs();

    return () => { };
  }, [conversations]);

  return (
    <aside className="sidemenu">
      <div className="sidemenu-button" onClick={createChat}>
        <AddOutlinedIcon />
        New Chat
      </div>
      {groupedConvs && Object.entries(groupedConvs).flatMap(([grp, convs]) => (
        [
          <div key={grp} className="sidemenu-date-group">{grp}</div>,
          convs.map((conv) => (<ChatTab key={conv.id} chat={conv} onConvDeleted={onConvDeleted} />))
        ]
      ))}
      <hr className="sidemenu-bottom" />
      <div className="sidemenu-bottom-group">
        <div className="sidemenu-bottom-group-items">
          <InfoOutlinedIcon />
        </div>
        <div className="sidemenu-bottom-group-items">
          <a className="link-icon" href="https://github.com/edwardzjl/chatbot" target="_blank" rel="noreferrer"> <GitHubIcon /> </a>
        </div>
        <div className="sidemenu-bottom-group-items">
          <a className="link-icon" href="mailto:jameszhou2108@hotmail.com">
            <MailOutlineIcon />
          </a>
        </div>
      </div>
    </aside>
  );
};

export default SideMenu;
