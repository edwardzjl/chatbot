import styles from "./index.module.css";

import { useEffect, useRef } from "react";
import PropTypes from "prop-types";


const FullScreenImage = ({ src, onClose = () => {}, className, ...props }) => {
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

    return (
        <div className={styles.fullScreenContainer} onClick={onClose}>
            <img
                ref={imageRef}
                className={`${styles.fullScreenImage} ${className || ""}`}
                src={src}
                {...props}
            />
        </div>
    );
};

FullScreenImage.propTypes = {
    src: PropTypes.string.isRequired,
    onClose: PropTypes.func,
    className: PropTypes.string,
};

export default FullScreenImage;
