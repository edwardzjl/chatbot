import styles from "./index.module.css";

import { useContext, useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { darcula, googlecode } from "react-syntax-highlighter/dist/esm/styles/hljs";
import PropTypes from "prop-types";

import { ThemeContext } from "@/contexts/theme";


const PeekDetails = ({ summary, content, peekHeight = "5rem" }) => {
    const { theme } = useContext(ThemeContext);
    const [markdownTheme, setMarkdownTheme] = useState(darcula);
    const contentRef = useRef(null);
    const [isOpen, setIsOpen] = useState(false);

    const toggleOpen = () => {
        setIsOpen(!isOpen);
    };

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

    useEffect(() => {
        if (!isOpen && contentRef.current) {
            contentRef.current.scrollTop = contentRef.current.scrollHeight - contentRef.current.clientHeight;
        } else if (isOpen && contentRef.current) {
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
                            return !inline && match ? (
                                <div>
                                    <div className={styles.codeTitle}>
                                        <div>{match[1]}</div>
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
