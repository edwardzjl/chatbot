import "./index.css";

import { forwardRef, useContext, useEffect, useRef, useState } from "react";
import { Link, NavLink, Outlet, redirect, useNavigate, useNavigation } from "react-router-dom";

import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

import GitHubIcon from "@mui/icons-material/GitHub";

import { SnackbarContext } from "contexts/snackbar";
import { ThemeContext } from "contexts/theme";
import { ConversationContext } from "contexts/conversation";
import { MessageContext } from "contexts/message";
import { WebsocketContext } from "contexts/websocket";

import ChatTab from "./SideMenuButton";


const Alert = forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});


export async function action({ request }) {
  if (request.method === "POST") {
    const conversation = await request.json();
    return redirect(`/conversations/${conversation.id}`);
  }
}

const Root = () => {
  const { groupedConvs, dispatch: dispatchConv } = useContext(ConversationContext);

  const { theme } = useContext(ThemeContext);
  const { snackbar, setSnackbar } = useContext(SnackbarContext);
  const { dispatch } = useContext(MessageContext);
  const [isReady, setIsReady] = useState(false);
  const ws = useRef(null);

  const delDialogRef = useRef();
  const [toDelete, setToDelete] = useState({});

  const navigate = useNavigate();
  const navigation = useNavigation();


  useEffect(() => {
    const conn = () => {
      const wsurl = window.location.origin.replace(/^http/, "ws") + "/api/chat";
      console.debug("connecting to", wsurl);
      ws.current = new WebSocket(wsurl);

      ws.current.onopen = () => {
        console.debug("connected to", wsurl);
        setIsReady(true);
      };
      ws.current.onclose = () => {
        console.debug("connection closed");
        setIsReady(false);
        setTimeout(() => {
          conn();
        }, 1000);
      };
      ws.current.onerror = (err) => {
        console.error("connection error", err);
        ws.current.close();
      };
      ws.current.onmessage = (event) => {
        // <https://react.dev/learn/queueing-a-series-of-state-updates>
        // <https://react.dev/learn/updating-arrays-in-state>
        try {
          const message = JSON.parse(event.data);
          switch (message.type) {
            case "text":
              dispatch({
                type: "added",
                message: message,
              });
              break;
            case "stream/start":
              dispatch({
                type: "added",
                // Initialize an empty content if undefined
                message: { content: message.content || "", ...message },
              });
              break;
            case "stream/text":
              dispatch({
                type: "appended",
                message: message,
              });
              break;
            case "stream/end":
              break;
            case "info":
              if (message.content.type === "title-generated") {
                dispatchConv({ type: "renamed", convId: message.conversation, title: message.content.payload });
              } else {
                console.log("unhandled info message", message);
              }
              break;
            case "error":
              setSnackbar({
                open: true,
                severity: "error",
                message: "Something goes wrong, please try again later.",
              });
              break;
            default:
              console.warn("unknown message type", message.type);
          }
        } catch (error) {
          console.debug("not a json message", event.data);
        }
      };
    }
    conn();

    return () => {
      ws.current.close();
    };
  }, []);

  const onDeleteClick = (id, title) => {
    setToDelete({ id, title });
    delDialogRef.current?.showModal();
  };

  const deleteConv = async (id) => {
    delDialogRef.current?.close();
    setToDelete({});
    await fetch(`/api/conversations/${id}`, {
      method: "DELETE",
    });
    dispatchConv({ type: "deleted", convId: id });
    navigate("/");
  };

  const closeSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <WebsocketContext.Provider value={[isReady, ws.current?.send.bind(ws.current)]}>
      <div className={`App theme-${theme}`}>
        <aside className="sidemenu">
          <Link className="sidemenu-button" to="/">
            <span class="material-symbols-outlined">chat_add_on</span>
            <span>New Chat</span>
          </Link>
          <nav>
            {groupedConvs && Object.entries(groupedConvs).flatMap(([grp, convs]) => (
              [
                <div key={grp}>
                  <div className="sidemenu-date-group">{grp}</div>
                  <ul>
                    {convs.map((conv) => (
                      <li key={conv.id}>
                        <NavLink
                          to={`conversations/${conv.id}`}
                          className={`sidemenu-button ${({ isActive, isPending }) => isActive ? "active" : isPending ? "pending" : ""}`}
                        >
                          {({ isActive, isPending, isTransitioning }) => (
                            <ChatTab chat={conv} isActive={isActive} onDeleteClick={onDeleteClick} />
                          )}
                        </NavLink>
                      </li>
                    ))}
                  </ul>
                </div>
              ]
            ))}
          </nav>
          <hr className="sidemenu-bottom" />
          <div className="sidemenu-bottom-group">
            <div className="sidemenu-bottom-group-items">
              <span class="material-symbols-outlined">info</span>
            </div>
            <div className="sidemenu-bottom-group-items">
              <a href="https://github.com/edwardzjl/chatbot" target="_blank" rel="noreferrer"> <GitHubIcon /> </a>
            </div>
            <div className="sidemenu-bottom-group-items">
              <a href="mailto:jameszhou2108@hotmail.com">
                <span class="material-symbols-outlined">mail</span>
              </a>
            </div>
          </div>
        </aside>
        <dialog
          className="del-dialog"
          ref={delDialogRef}
        >
          <h2>Delete conversation?</h2>
          <p>This will delete "{toDelete.title}"</p>
          <div className="del-dialog-actions">
            <button autoFocus onClick={() => deleteConv(toDelete.id)}>Delete</button>
            <button onClick={() => delDialogRef.current?.close()}>Cancel</button>
          </div>
        </dialog>
        {/* TODO: this loading state will render the delete dialog */}
        <section className={`chatbox ${navigation.state === "loading" ? "loading" : ""}`}>
          <Outlet />
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
    </WebsocketContext.Provider>
  );
}

export default Root;
