import "./App.css";
import { forwardRef, useContext, useEffect, useState } from "react";

import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

import SideMenu from "components/SideMenu";
import ChatLog from "components/ChatLog";
import ChatMessage from "components/ChatLog/ChatMessage";
import ChatInput from "components/ChatLog/ChatInput";

import { ConversationContext } from "contexts/conversation";
import { SnackbarContext } from "contexts/snackbar";


const Alert = forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});


const App = () => {
  const [conversations,] = useContext(ConversationContext);
  const [snackbar, setSnackbar] = useContext(SnackbarContext);

  const [currentConv, setCurrentConv] = useState(
    /** @type {{id: string, title: string?, messages: Array}} */ {}
  );
  useEffect(() => {
    if (conversations?.length > 0) {
      const currentConv = conversations.find((c) => c.active);
      setCurrentConv(currentConv);
    }
  }, [conversations]);

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
