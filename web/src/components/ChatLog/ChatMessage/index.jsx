import "./index.css";

import { useState } from "react";
import Markdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import { darcula } from "react-syntax-highlighter/dist/esm/styles/hljs";

import Avatar from "@mui/material/Avatar";
import Tooltip from "@mui/material/Tooltip";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";

import { getFirstLetters, stringToColor } from "commons";

/**
 *
 * @param {object} message
 * @param {string} message.from
 * @param {string} message.content
 * @returns
 */
const ChatMessage = ({ message }) => {
  const [copyTooltipTitle, setCopyTooltipTitle] = useState("copy content");

  const onCopyClick = () => {
    navigator.clipboard.writeText(message.content);
    setCopyTooltipTitle("copied!");
  };

  /**
   * Checks whether a message is sent by bot.
   * @param {*} message
   */
  const botMessage = (message) => {
    const msgFrom = message.from.toLowerCase();
    return msgFrom === "ai" || msgFrom === "assistant";
  };

  return (
    <div className={`chat-message ${botMessage(message) && "AI"}`}>
      <div
        className="chat-message-center"
        onMouseEnter={() => setCopyTooltipTitle("copy content")}
      >
        <Avatar
          className="chat-message-avatar"
          // Cannot handle string to color in css
          sx={{
            bgcolor: stringToColor(message.from),
          }}
        >
          {botMessage(message)
            ? "AI"
            : getFirstLetters(message.from)}
        </Avatar>
        <Markdown
          className="chat-message-content"
          remarkPlugins={[remarkGfm]}
          components={{
            code({ inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || "");
              return !inline && match ? (
                <SyntaxHighlighter
                  {...props}
                  style={darcula}
                  language={match[1]}
                  PreTag="div"
                >
                  {/* remove the last line separator, is it necessary? */}
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
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
        {botMessage(message) && (
          <Tooltip title={copyTooltipTitle}>
            <ContentCopyIcon
              className="chat-message-content-copy"
              onClick={onCopyClick}
            />
          </Tooltip>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
