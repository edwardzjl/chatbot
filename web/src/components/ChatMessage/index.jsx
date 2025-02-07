import styles from './index.module.css';

import { useContext, useEffect, useState } from "react";
import Markdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { darcula, googlecode } from "react-syntax-highlighter/dist/esm/styles/hljs";
import PropTypes from "prop-types";

import Avatar from "@mui/material/Avatar";
import Tooltip from "@mui/material/Tooltip";

import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import ThumbUpIcon from "@mui/icons-material/ThumbUp";
import ThumbUpOutlined from "@mui/icons-material/ThumbUpOutlined";
import ThumbDownIcon from "@mui/icons-material/ThumbDown";
import ThumbDownOutlined from "@mui/icons-material/ThumbDownOutlined";

import { ThemeContext } from "@/contexts/theme";
import { MessageContext } from "@/contexts/message";
import { UserContext } from "@/contexts/user";
import { stringToColor } from "@/commons";


/**
 * ChatMessage component that displays a single chat message along with relevant actions such as copying content,
 * giving thumbs up/down feedback, and rendering markdown content with syntax highlighting.
 *
 * @param {Object} props - The component props.
 * @param {string} props.convId - The conversation ID.
 * @param {Object} props.message - The message object containing details like the sender, content, and feedback.
 * @param {string} props.message.from - The sender of the message (either "You" or "AI").
 * @param {string} props.message.content - The message content, which can include markdown.
 * @returns {JSX.Element} The rendered ChatMessage component.
 */
const ChatMessage = ({ convId, message }) => {
  const { theme } = useContext(ThemeContext);
  const [markdownTheme, setMarkdownTheme] = useState(darcula);
  const { username, avatar } = useContext(UserContext);
  const { dispatch } = useContext(MessageContext);
  const [copyTooltipTitle, setCopyTooltipTitle] = useState("copy content");
  const [thumbUpTooltipTitle, setThumbUpTooltipTitle] = useState("good answer");
  const [thumbDownTooltipTitle, setThumbDownTooltipTitle] = useState("bad answer");

  // Update markdown theme based on the current theme
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

  /**
   * Handles the copying of message content to the clipboard.
   * Updates the tooltip title to indicate the content has been copied.
   *
   * @param {string} content - The content to be copied to the clipboard.
   */
  const onCopyClick = (content) => {
    navigator.clipboard.writeText(content);
    setCopyTooltipTitle("copied!");
    setTimeout(() => {
      setCopyTooltipTitle("copy content");
    }, 3000);
  };

  /**
   * Handles the thumbs up action by sending a PUT request to register the feedback.
   * Updates the tooltip and dispatches a message update to the context.
   */
  const onThumbUpClick = () => {
    fetch(`/api/conversations/${convId}/messages/${message.id}/thumbup`, {
      method: "PUT",
    }).then(() => {
      setThumbUpTooltipTitle("thanks!");
      dispatch({
        type: "updated",
        message: { ...message, feedback: "thumbup" },
      });
    });
  };

  /**
   * Handles the thumbs down action by sending a PUT request to register the feedback.
   * Updates the tooltip and dispatches a message update to the context.
   */
  const onThumbDownClick = () => {
    fetch(`/api/conversations/${convId}/messages/${message.id}/thumbdown`, {
      method: "PUT",
    }).then(() => {
      setThumbDownTooltipTitle("thanks!");
      dispatch({
        type: "updated",
        message: { ...message, feedback: "thumbdown" },
      });
    });
  };

  /**
   * Determines if the message was sent by the current user.
   *
   * @param {Object} message - The message object.
   * @returns {boolean} True if the message was sent by the current user, otherwise false.
   */
  const myMessage = message.from.toLowerCase() === username;

  return (
    <div className={`${styles.messageContainer} ${myMessage ? styles.mine : ""}`}>
      <div className={styles.messageTitle}>
        {/* NOTE: className not working on Avatar */}
        {myMessage ?
          <Avatar src={avatar} /> :
          // TODO: give AI an avatar
          <Avatar sx={{ bgcolor: stringToColor(message.from) }}>
            AI
          </Avatar>
        }
        <div className={styles.messageTitleName}>{myMessage ? "You" : "AI"}</div>
      </div>
      <div className={styles.messageBody}>
        <Markdown
          className={styles.messageContent}
          remarkPlugins={[remarkGfm, remarkMath]}
          rehypePlugins={[rehypeKatex]}
          components={{
            code({ inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || "");
              return !inline && match ? (
                <div>
                  <div className={styles.messageCodeTitle}>
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
        {!myMessage && (
          <div className={styles.messageFeedbacks}>
            <Tooltip title={copyTooltipTitle}>
              <ContentCopyIcon onClick={() => onCopyClick(message.content)} />
            </Tooltip>
            {message.feedback === "thumbdown" ? undefined : message.feedback === "thumbup" ? <ThumbUpIcon /> :
              <Tooltip title={thumbUpTooltipTitle}>
                <ThumbUpOutlined onClick={onThumbUpClick} />
              </Tooltip>
            }
            {message.feedback === "thumbup" ? undefined : message.feedback === "thumbdown" ? <ThumbDownIcon /> :
              <Tooltip title={thumbDownTooltipTitle}>
                <ThumbDownOutlined onClick={onThumbDownClick} />
              </Tooltip>
            }
          </div>
        )}
      </div>
    </div>
  );
};

ChatMessage.propTypes = {
  convId: PropTypes.string,
  message: PropTypes.object.isRequired,
};

export default ChatMessage;
