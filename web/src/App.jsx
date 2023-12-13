import "./App.css";
import { forwardRef, useContext } from "react";

import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

import SideMenu from "components/SideMenu";
import ChatboxHeader from "components/ChatboxHeader";
import ChatLog from "components/ChatLog";
import ChatMessage from "components/ChatLog/ChatMessage";
import ChatInput from "components/ChatInput";

import { ConversationContext } from "contexts/conversation";
import { SnackbarContext } from "contexts/snackbar";
import { ThemeContext } from "contexts/theme";


const Alert = forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});


const App = () => {
  const { theme } = useContext(ThemeContext);
  const { currentConv } = useContext(ConversationContext);
  const { snackbar, setSnackbar } = useContext(SnackbarContext);

  const closeSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <div className={`App theme-${theme}`}>
      <SideMenu />
      <section className="chatbox">
        <ChatboxHeader />
        <ChatLog>
          {currentConv && currentConv.messages && currentConv.messages.map((message, index) => (
            <ChatMessage key={index} convId={currentConv.id} idx={index} message={message} />
          ))}
        </ChatLog>
        <ChatInput />
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
