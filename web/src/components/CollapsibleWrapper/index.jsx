import { useEffect, useState } from "react";
import PropTypes from "prop-types";


const DEFAULT_COLLAPSE_THRESHOLD = 768;


const CollapsibleWrapper = ({
    children,
    collapseThreshold = DEFAULT_COLLAPSE_THRESHOLD
}) => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    useEffect(() => {
        const handleResize = () => {
            setIsCollapsed(window.innerWidth < collapseThreshold);
        };

        handleResize();

        window.addEventListener("resize", handleResize);

        return () => {
            window.removeEventListener("resize", handleResize);
        };
    }, [collapseThreshold]);

    const toggle = () => {
        setIsCollapsed(!isCollapsed);
    };

    return children({ isCollapsed, toggle });
};

CollapsibleWrapper.propTypes = {
    children: PropTypes.func.isRequired,
    collapseThreshold: PropTypes.number,
};

export default CollapsibleWrapper;
