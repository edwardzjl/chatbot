import styles from "./index.module.css";

import { useEffect, useRef } from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";


const FullScreenImage = ({ src, onClose = () => { }, className, ...props }) => {
    const imageRef = useRef(null);

    useEffect(() => {
        const handleKeyDown = (event) => {
            if (event.key === "Escape") {
                onClose();
            }
        };

        window.addEventListener("keydown", handleKeyDown);

        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    }, [onClose]);

    const backdropClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    const content = (
        <div
            className={styles.fullScreenContainer}
            onClick={backdropClick}
            role="dialog"
            aria-modal="true"
            aria-label={props.alt || "Image preview"}
            tabIndex={-1}
        >
            <img
                ref={imageRef}
                className={`${styles.fullScreenImage} ${className || ""}`}
                src={src}
                {...props}
            />
        </div>
    );

    return ReactDOM.createPortal(content, document.body);
};

FullScreenImage.propTypes = {
    src: PropTypes.string.isRequired,
    onClose: PropTypes.func,
    className: PropTypes.string,
};

export default FullScreenImage;
