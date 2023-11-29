import "./index.css";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import { darcula } from "react-syntax-highlighter/dist/esm/styles/prism";

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
        <ReactMarkdown
          className="chat-message-content"
          children={message.content}
          remarkPlugins={[remarkGfm]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || "");
              return !inline && match ? (
                <SyntaxHighlighter
                  {...props}
                  children={String(children).replace(/\n$/, "")}
                  style={darcula}
                  language={match[1]}
                  PreTag="div"
                />
              ) : (
                <code {...props} className={className}>
                  {children}
                </code>
              );
            },
          }}
        />
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
