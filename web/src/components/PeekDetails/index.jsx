import styles from "./index.module.css";

import { useContext, useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import PropTypes from "prop-types";

import { ThemeContext } from "@/contexts/theme";


const PeekDetails = ({ summary, content, peekHeight = "5rem" }) => {
    const { codeTheme } = useContext(ThemeContext);
    const contentRef = useRef(null);
    const [isOpen, setIsOpen] = useState(false);

    const toggleOpen = () => {
        setIsOpen(!isOpen);
    };

    useEffect(() => {
        if (!contentRef.current) {
            return;
        }
        if (!isOpen) {
            contentRef.current.scrollTop = contentRef.current.scrollHeight - contentRef.current.clientHeight;
        } else {
            contentRef.current.scrollTop = 0;
        }
    }, [isOpen, content]);

    return (
        <div className={styles.peekDetails}>
            <div className={styles.summaryBar} onClick={toggleOpen}>
                {summary}
                <span className={styles.toggleIcon}>{isOpen ? "-" : "+"}</span>
            </div>
            <div
                className={styles.content}
                style={{
                    maxHeight: isOpen ? "200rem" : peekHeight  // I must use a numeric value for transition to work
                }}
                ref={contentRef}
            >
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
                        },
                    }}
                >
                    {content}
                </Markdown>
            </div>
        </div>
    );
};

PeekDetails.propTypes = {
    summary: PropTypes.string.isRequired,
    content: PropTypes.string,
    peekHeight: PropTypes.string,
};

export default PeekDetails;
