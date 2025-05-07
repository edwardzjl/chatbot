import styles from "./MarkdownContent.module.css";

import { useContext, useState } from "react";
import PropTypes from "prop-types";

import Markdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

import Tooltip from "@mui/material/Tooltip";

import ContentCopyIcon from "@mui/icons-material/ContentCopy";

import { ThemeContext } from "@/contexts/theme";


const MarkdownContent = ({content}) => {
    const { codeTheme } = useContext(ThemeContext);
    const [copyTooltipTitle, setCopyTooltipTitle] = useState("copy content");

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

    return (
        <Markdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeKatex]}
            components={{
                code({ inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || "");
                    if (inline || !match) {
                        return <code {...props} className={className}>{children}</code>;
                    }
                    const language = match[1];
                    return (
                        <div>
                            <div className={styles.codeTitle}>
                                <div>{language}</div>
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
                                language={language}
                                PreTag="div"
                            >
                                {/* remove the last line separator, is it necessary? */}
                                {String(children).replace(/\n$/, "")}
                            </SyntaxHighlighter>
                        </div>
                    );
                }
            }}
        >
            {content}
        </Markdown>
    );
};

MarkdownContent.propTypes = {
    content: PropTypes.string,
};

export default MarkdownContent;
