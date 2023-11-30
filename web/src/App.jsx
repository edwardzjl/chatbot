import "./App.css";
import { forwardRef, useContext, useEffect, useState } from "react";

import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

import SideMenu from "components/SideMenu";
import ChatLog from "components/ChatLog";
import ChatMessage from "components/ChatLog/ChatMessage";
import ChatInput from "components/ChatLog/ChatInput";
import generateName from "names";
import {
  createConversation,
  getConversations,
  getConversation,
} from "requests";
import { ConversationContext } from "contexts/conversation";
import { SnackbarContext } from "contexts/snackbar";
import { UserContext } from "contexts/user";
import { WebsocketContext } from "contexts/websocket";
import { getCurrentConversation } from "conversationsReducer";

const Alert = forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});


const App = () => {
  const [, setUsername] = useContext(UserContext);
  const [, val,] = useContext(WebsocketContext);
  const [conversations, dispatch] = useContext(ConversationContext);
  const [snackbar, setSnackbar] = useContext(SnackbarContext);

  useEffect(() => {
    // <https://react.dev/learn/queueing-a-series-of-state-updates>
    // <https://react.dev/learn/updating-arrays-in-state>
    try {
      const { type, conversation, from, content } = JSON.parse(val);
      switch (type) {
        case "start":
          dispatch({
            type: "messageAdded",
            id: conversation,
            message: { from: from, content: content || "", type: "stream" },
          });
          break;
        case "stream":
          dispatch({
            type: "messageAppended",
            id: conversation,
            message: { from: from, content: content, type: "stream" },
          });
          break;
        case "error":
          setSnackbar({
            open: true,
            severity: "error",
            message: "Something goes wrong, please try again later.",
          });
          break;
        case "text":
          dispatch({
            type: "messageAdded",
            id: conversation,
            message: { from: from, content: content, type: "text" },
          });
          break;
        case "end":
          break;
        default:
          console.warn("unknown message type", type);
      }
    } catch (error) {
      console.debug("not a json message", val);
    }
  }, [val]);

  const [currentConv, setCurrentConv] = useState(
    /** @type {{id: string, title: string?, messages: Array}} */ {}
  );
  useEffect(() => {
    if (conversations?.length > 0) {
      const currentConv = getCurrentConversation(conversations);
      setCurrentConv(currentConv);
    }
  }, [conversations]);

  // initialization
  useEffect(() => {
    const initialization = async () => {
      let _username;
      const res = await fetch("/api/userinfo");
      if (res.ok) {
        const data = await res.json();
        if (data.username) {
          _username = data.username;
        } else {
          _username = generateName();
        }
      } else {
        console.error("error getting userinfo, generating fake user", res);
        _username = generateName();
      }
      setUsername(_username);

      let convs = await getConversations();
      if (convs.length > 0) {
        dispatch({
          type: "replaceAll",
          conversations: convs,
        });
      } else {
        console.log("no chats, initializing a new one");
        const conv = await createConversation();
        dispatch({
          type: "added",
          conversation: conv,
        });
        convs = [conv];
      }

      const activated = convs[0];
      const detailedConv = await getConversation(activated.id);
      dispatch({
        type: "updated",
        conversation: {
          ...detailedConv,
          messages: detailedConv.messages,
        },
      });
    };

    initialization();

    return () => { };
  }, []);

  const closeSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <div className="App">
      <SideMenu />
      <section className="chatbox">
        <ChatLog>
          {currentConv && currentConv.messages && currentConv.messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
        </ChatLog>
        <ChatInput chatId={currentConv?.id} />
      </section>
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

export default App;
