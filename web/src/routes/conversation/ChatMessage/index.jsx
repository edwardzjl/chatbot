import "./index.css";

import { useContext, useEffect, useState } from "react";
import Markdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import { darcula, googlecode } from "react-syntax-highlighter/dist/esm/styles/hljs";

import Avatar from "@mui/material/Avatar";
import Tooltip from "@mui/material/Tooltip";

import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import ThumbUpIcon from "@mui/icons-material/ThumbUp";
import ThumbUpOutlined from "@mui/icons-material/ThumbUpOutlined";
import ThumbDownIcon from "@mui/icons-material/ThumbDown";
import ThumbDownOutlined from "@mui/icons-material/ThumbDownOutlined";

import { ThemeContext } from "contexts/theme";
import { MessageContext } from "contexts/message";
import { UserContext } from "contexts/user";
import { getFirstLetters, stringToColor } from "commons";

/**
 * @param {string} convId
 * @param {integer} idx
 * @param {object} message
 * @param {string} message.from
 * @param {string} message.content
 * @returns
 */
const ChatMessage = ({ convId, idx, message }) => {
  const { theme } = useContext(ThemeContext);
  const [markdownTheme, setMarkdownTheme] = useState(darcula);
  const { username } = useContext(UserContext);
  const { dispatch } = useContext(MessageContext);
  const [copyTooltipTitle, setCopyTooltipTitle] = useState("copy content");
  const [thumbUpTooltipTitle, setThumbUpTooltipTitle] = useState("good answer");
  const [thumbDownTooltipTitle, setThumbDownTooltipTitle] = useState("bad answer");

  useEffect(() => {
    switch (theme) {
      case "dark":
        setMarkdownTheme(darcula);
        break;
      case "light":
        setMarkdownTheme(googlecode);
        break;
      default: {
        if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
          setMarkdownTheme(darcula);
        } else {
          setMarkdownTheme(googlecode);
        }
      }
    }
  }, [theme]);

  const onCopyClick = (content) => {
    navigator.clipboard.writeText(content);
    setCopyTooltipTitle("copied!");
    setTimeout(() => {
      setCopyTooltipTitle("copy content");
    }, "3000");
  };
  const onThumbUpClick = () => {
    fetch(`/api/conversations/${convId}/messages/${idx}/thumbup`, {
      method: "PUT",
    }).then(() => {
      setThumbUpTooltipTitle("thanks!");
      dispatch({
        type: "feedback",
        idx: idx,
        feedback: "thumbup",
      });
    });
  };
  const onThumbDownClick = () => {
    fetch(`/api/conversations/${convId}/messages/${idx}/thumbdown`, {
      method: "PUT",
    }).then(() => {
      setThumbDownTooltipTitle("thanks!");
      dispatch({
        type: "feedback",
        idx: idx,
        feedback: "thumbdown",
      });
    });
  };

  /**
   * Checks whether a message is sent by me.
   * @param {*} message
   */
  const myMessage = (message) => {
    const msgFrom = message.from.toLowerCase();
    return msgFrom === username;
  };

  return (
    <div className={`message-container ${myMessage(message) && "mine"}`}>
      <div className="message-title">
        <Avatar
          className="message-title-avatar"
          // Cannot handle string to color in css
          sx={{
            bgcolor: stringToColor(message.from),
          }}
        >
          {myMessage(message) ? getFirstLetters(message.from) : "AI"}
        </Avatar>
        <div className="message-title-name">{myMessage(message) ? "You" : "AI"}</div>
      </div>
      <div className="message-body">
        <Markdown
          className="message-content"
          remarkPlugins={[remarkGfm]}
          components={{
            code({ inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || "");
              return !inline && match ? (
                <div>
                  <div className="message-code-title">
                    <div>{match[1]}</div>
                    <Tooltip title={copyTooltipTitle}>
                      <ContentCopyIcon onClick={() => onCopyClick(children)} />
                    </Tooltip>
                  </div>
                  <SyntaxHighlighter
                    {...props}
                    style={markdownTheme}
                    language={match[1]}
                    PreTag="div"
                  >
                    {/* remove the last line separator, is it necessary? */}
                    {String(children).replace(/\n$/, "")}
                  </SyntaxHighlighter>
                </div>
              ) : (
                <code {...props} className={className}>
                  {children}
                </code>
              );
            },
          }}
        >
          {message.content}
        </Markdown>
        {!myMessage(message) && (
          <div className="message-feedbacks">
            <Tooltip title={copyTooltipTitle}>
              <ContentCopyIcon className="message-feedback" onClick={() => onCopyClick(message.content)} />
            </Tooltip>
            {message.feedback === "thumbdown" ? undefined : message.feedback === "thumbup" ? <ThumbUpIcon className="message-feedback" /> :
              <Tooltip title={thumbUpTooltipTitle}>
                <ThumbUpOutlined className="message-feedback" onClick={onThumbUpClick} />
              </Tooltip>
            }
            {message.feedback === "thumbup" ? undefined : message.feedback === "thumbdown" ? <ThumbDownIcon className="message-feedback" /> :
              <Tooltip title={thumbDownTooltipTitle}>
                <ThumbDownOutlined className="message-feedback" onClick={onThumbDownClick} />
              </Tooltip>
            }
          </div>
        )}
      </div>

    </div>
  );
};

export default ChatMessage;
