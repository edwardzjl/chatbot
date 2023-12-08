import "./index.css";

import { useContext, useState } from "react";
import Markdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import { darcula, googlecode } from "react-syntax-highlighter/dist/esm/styles/hljs";

import Avatar from "@mui/material/Avatar";
import Tooltip from "@mui/material/Tooltip";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import ThumbUpOutlined from "@mui/icons-material/ThumbUpOutlined";
import ThumbDownOutlined from "@mui/icons-material/ThumbDownOutlined";

import { ThemeContext } from "contexts/theme";
import { getFirstLetters, stringToColor } from "commons";

/**
 *
 * @param {object} message
 * @param {string} message.from
 * @param {string} message.content
 * @returns
 */
const ChatMessage = ({ message }) => {
  const [theme, ,] = useContext(ThemeContext);
  const [copyTooltipTitle, setCopyTooltipTitle] = useState("copy content");
  const [thumbUpTooltipTitle, setThumbUpTooltipTitle] = useState("good answer");
  const [thumbDownTooltipTitle, setThumbDownTooltipTitle] = useState("bad answer");

  const onCopyClick = (content) => {
    navigator.clipboard.writeText(content);
    setCopyTooltipTitle("copied!");
    setTimeout(() => {
      setCopyTooltipTitle("copy content");
    }, "3000");
  };
  const onThumbUpClick = () => {
    setThumbUpTooltipTitle("thanks!");
    setTimeout(() => {
      setThumbUpTooltipTitle("good answer");
    }, "3000");
  };
  const onThumbDownClick = () => {
    setThumbDownTooltipTitle("thanks!");
    setTimeout(() => {
      setThumbUpTooltipTitle("bad answer");
    }, "3000");
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
    <div className={`message-container ${botMessage(message) && "AI"}`}>
      <div className="message-title">
        <Avatar
          className="message-title-avatar"
          // Cannot handle string to color in css
          sx={{
            bgcolor: stringToColor(message.from),
          }}
        >
          {botMessage(message) ? "AI" : getFirstLetters(message.from)}
        </Avatar>
        <div className="message-title-name">{botMessage(message) ? "AI" : "You"}</div>
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
                    style={theme === "dark" ? darcula : googlecode}
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
        {botMessage(message) && (
          <div className="message-feedbacks">
            <Tooltip title={copyTooltipTitle}>
              <ContentCopyIcon className="message-feedback" onClick={() => onCopyClick(message.content)} />
            </Tooltip>
            <Tooltip title={thumbUpTooltipTitle}>
              <ThumbUpOutlined className="message-feedback" onClick={onThumbUpClick} />
            </Tooltip>
            <Tooltip title={thumbDownTooltipTitle}>
              <ThumbDownOutlined className="message-feedback" onClick={onThumbDownClick} />
            </Tooltip>
          </div>
        )}
      </div>

    </div>
  );
};

export default ChatMessage;
