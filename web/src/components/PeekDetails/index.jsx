import styles from "./index.module.css";

import { useEffect, useRef, useState } from "react";

import PropTypes from "prop-types";


const PeekDetails = ({ summary, children, peekHeight = "5rem" }) => {

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
    }, [isOpen, children]);

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
                {children}
            </div>
        </div>
    );
};

PeekDetails.propTypes = {
    summary: PropTypes.string.isRequired,
    children: PropTypes.node.isRequired,
    peekHeight: PropTypes.string,
};

export default PeekDetails;
