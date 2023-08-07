import "./normal.css";
import "./App.css";
import { useState, useEffect, useReducer, forwardRef } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";

import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

import SideMenu from "components/SideMenu";
import ChatLog from "components/ChatLog";
import ChatMessage from "components/ChatMessage";
import ChatInput from "components/ChatInput";
import generateName from "names";
import {
  createConversation,
  getConversations,
  getConversation,
} from "requests";
import { UserContext, ConversationContext, SnackbarContext } from "contexts";
import {
  conversationsReducer,
  getCurrentConversation,
} from "conversationsReducer";

const Alert = forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

/**
 * Backend does not store real username in messages, we need to update it.
 * @param {*} message
 * @param {*} username
 * @returns
 */
const replaceUsername = (message, username) => {
  if (message.from === "human") {
    return { ...message, from: username };
  } else {
    return message;
  }
};

function App() {
  const [username, setUsername] = useState("");

  /**
   * All conversations of the current user.
   */
  const [conversations, dispatch] = useReducer(
    conversationsReducer,
    /** @type {[{id: string, title: string?, messages: Array, active: boolean}]} */
    []
  );

  const [currentConv, setCurrentConv] = useState(
    /** @type {{id: string, title: string?, messages: Array}} */ {}
  );
  useEffect(() => {
    if (conversations?.length > 0) {
      const currentConv = getCurrentConversation(conversations);
      setCurrentConv(currentConv);
    }
  }, [conversations]);

  /**
   * open, severity, message
   */
  const [snackbar, setSnackbar] = useState(
    /** @type {{open: boolean, severity: string?, message: string}} */ {}
  );

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
          messages: detailedConv.messages.map((message) =>
            replaceUsername(message, username)
          ),
        },
      });
    };

    initialization();

    return () => {};
  }, []);

  const sendMessage = async (convId, message) => {
    fetchEventSource(`/api/conversations/${convId}/messages`, {
      method: "POST",
      headers: {
        Accept: "text/event-stream",
        "Content-Type": "application/json",
        // TODO: remove this header when we add auth back
        "kubeflow-userid": username,
      },
      body: JSON.stringify({
        message: message,
      }),
      openWhenHidden: true,
      async onopen(response) {
        if (
          response.ok &&
          response.headers.get("content-type") === "text/event-stream"
        ) {
          console.log("on open");
          // add a blank message to the chatlog
          dispatch({
            type: "messageAdded",
            id: convId,
            message: { from: "AI", content: "" },
          });
        } else {
          console.error("error opening the SSE endpoint", response);
        }
      },
      onmessage(msg) {
        // <https://react.dev/learn/queueing-a-series-of-state-updates>
        // <https://react.dev/learn/updating-arrays-in-state>
        try {
          const payload = JSON.parse(msg.data);
          dispatch({
            type: "messageAppended",
            id: convId,
            message: { from: "AI", content: payload.text },
          });
        } catch (error) {
          console.debug("not a json message", msg);
        }
      },
      onclose() {
        console.log("on close");
      },
      onerror(err) {
        console.error("on error", err);
      },
    });
  };

  const closeSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <div className="App">
      <SnackbarContext.Provider value={setSnackbar}>
        <UserContext.Provider value={username}>
          <ConversationContext.Provider value={{ conversations, dispatch }}>
            <SideMenu />
            <section className="chatbox">
              <ChatLog>
                {currentConv?.messages?.map(
                  (message, index) => (
                    <ChatMessage key={index} message={message} />
                  )
                )}
              </ChatLog>
              <ChatInput
                chatId={currentConv?.id}
                onSend={sendMessage}
              />
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
          </ConversationContext.Provider>
        </UserContext.Provider>
      </SnackbarContext.Provider>
    </div>
  );
}

export default App;
