import styles from "./index.module.css";

import { useState } from "react";
import PropTypes from "prop-types";

import FullScreenImage from "@/components/FullScreenImage";


const PreviewImage = ({ src, className, alt, previewProps = {}, ...props }) => {
    const [fullScreen, setFullScreen] = useState(false);

    const handleImageClick = () => {
        setFullScreen(true);
    };

    const handleCloseFullScreen = () => {
        setFullScreen(false);
    };

    return (
        <>
            <img
                src={src}
                className={`${styles.overview} ${className || ""}`}
                onClick={handleImageClick}
                alt={alt}
                {...props}
            />
            {fullScreen && (
                <FullScreenImage
                    src={src}
                    onClose={handleCloseFullScreen}
                    alt={alt}
                    {...previewProps}
                />
            )}
        </>
    );
};

PreviewImage.propTypes = {
    src: PropTypes.string.isRequired,
    className: PropTypes.string,
    alt: PropTypes.string,
    previewProps: PropTypes.object,
};

export default PreviewImage;
