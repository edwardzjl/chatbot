import styles from './index.module.css';

import { useContext, useState } from "react";
import Markdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import PropTypes from "prop-types";

import Avatar from "@mui/material/Avatar";
import Tooltip from "@mui/material/Tooltip";

import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import ThumbUpIcon from "@mui/icons-material/ThumbUp";
import ThumbUpOutlined from "@mui/icons-material/ThumbUpOutlined";
import ThumbDownIcon from "@mui/icons-material/ThumbDown";
import ThumbDownOutlined from "@mui/icons-material/ThumbDownOutlined";

import { MessageContext } from "@/contexts/message";
import { SnackbarContext } from "@/contexts/snackbar";
import { ThemeContext } from "@/contexts/theme";
import { UserContext } from "@/contexts/user";

import PeekDetails from "@/components/PeekDetails";
import PreviewImage from "@/components/PreviewImage";

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
    const { codeTheme } = useContext(ThemeContext);
    const { username, avatar } = useContext(UserContext);
    const { setSnackbar } = useContext(SnackbarContext);
    const { dispatch } = useContext(MessageContext);
    const [copyTooltipTitle, setCopyTooltipTitle] = useState("copy content");
    const [feedbackTooltipTitles, setFeedbackTooltipTitles] = useState({ thumbup: "I like it!", thumbdown: "Not so good" });

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
     * Handles the thumbs up/down feedback action by sending a PUT request to register the feedback.
     * Updates the tooltip and dispatches a message update to the context.
     *
     * @param {string} feedback - "thumbup" or "thumbdown"
     */
    const onFeedback = async (feedback) => {
        try {
            await fetch(`/api/conversations/${convId}/messages/${message.id}/${feedback}`, {
                method: "PUT",
            });
            dispatch({
                type: "updated",
                message: { ...message, feedback: feedback },
            });
            setFeedbackTooltipTitles((prev) => ({ ...prev, [feedback]: "thanks!" }));
        } catch (error) {
            console.error(error);
            setSnackbar({
                open: true,
                severity: "error",
                message: "An error occurred, please try again later.",
            });
        }
    };

    /**
     * Determines if the message was sent by the current user.
     *
     * @param {Object} message - The message object.
     * @returns {boolean} True if the message was sent by the current user, otherwise false.
     */
    const myMessage = message.from && message.from.toLowerCase() === username;

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
                {message.additional_kwargs && message.additional_kwargs.thought && (
                    <PeekDetails
                        summary="Thoughts"
                        content={message.additional_kwargs.thought}
                    />
                )}
                <Markdown
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
                                            <ContentCopyIcon
                                                aria-label="Copy code snippet to clipboard"
                                                onClick={() => onCopyClick(children)}
                                            />
                                        </Tooltip>
                                    </div>
                                    <SyntaxHighlighter
                                        {...props}
                                        style={codeTheme}
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
                    {message.content || ""}
                </Markdown>
                {message.attachments &&
                    <div className={styles.attachments}>
                        {message.attachments.map((attachment, index) => (
                            <div
                                key={index}
                                className={styles.attachment}
                            >
                                {/* These are blob urls, which does not support request params. */}
                                <PreviewImage
                                    className={styles.preview}
                                    srcSet={attachment.localUrl || attachment.url}
                                    src={attachment.localUrl || attachment.url}
                                    alt={attachment.name}
                                    loading="lazy"
                                />
                            </div>))
                        }
                    </div>
                }
                {!myMessage && (
                    <div className={styles.messageFeedbacks}>
                        <Tooltip title={copyTooltipTitle}>
                            <ContentCopyIcon
                                aria-label="Copy message content to clipboard"
                                onClick={() => onCopyClick(message.content)}
                            />
                        </Tooltip>
                        {message.feedback !== "thumbdown" && (
                            message.feedback === "thumbup" ? <ThumbUpIcon /> :
                                <Tooltip title={feedbackTooltipTitles.thumbup}>
                                    <ThumbUpOutlined
                                        aria-label="Mark this answer as good"
                                        onClick={() => onFeedback("thumbup")}
                                    />
                                </Tooltip>
                        )}
                        {message.feedback !== "thumbup" && (
                            message.feedback === "thumbdown" ? <ThumbDownIcon /> :
                                <Tooltip title={feedbackTooltipTitles.thumbdown}>
                                    <ThumbDownOutlined
                                        aria-label="Mark this answer as bad"
                                        onClick={() => onFeedback("thumbdown")}
                                    />
                                </Tooltip>
                        )}
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
