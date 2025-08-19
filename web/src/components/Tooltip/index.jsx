import styles from "./index.module.css";

import { useCallback, useEffect, useState, useRef, useId } from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";

import { cx } from "@/commons";


const Tooltip = ({
    children,
    text,
    delay = 500,
    hideDelay = 100,
    className,
    position = "top",
    offset = { x: 0, y: 0 }
}) => {
    const [isVisible, setIsVisible] = useState(false);
    const [stylePos, setStylePos] = useState({ top: 0, left: 0, transform: "" });
    const showTimer = useRef(null);
    const hideTimer = useRef(null);
    const triggerRef = useRef(null);
    const tooltipRef = useRef(null);
    const tooltipId = useId();
    const baseGap = 8;

    // Computes and updates the tooltip's viewport-based position.
    // Assumes the tooltip element itself uses `position: fixed`,
    // so `getBoundingClientRect()` coordinates can be used directly without adding scroll offsets.
    const computePosition = useCallback((pos = position) => {
        const el = triggerRef.current;
        if (!el) return;

        // Viewport-relative bounding box of the trigger element.
        // This moves as the page scrolls, so we recompute on scroll/resize.
        const rect = el.getBoundingClientRect();

        // Base transform: defines the tooltip's anchor point relative to (left, top).
        // e.g., for "top" we anchor the bottom-center of the tooltip to (left, top).
        const baseTransform = ({
            top: "translate(-50%, -100%)",
            bottom: "translate(-50%, 0)",
            left: "translate(-100%, -50%)",
            right: "translate(0, -50%)",
            "top-left": "translate(0, -100%)",
            "top-right": "translate(-100%, -100%)",
            "bottom-left": "translate(0, 0)",
            "bottom-right": "translate(-100%, 0)",
        }[pos]) || "translate(-50%, 0)";

        // Compute the base (left, top) in viewport coordinates (no scroll added).
        // `baseGap` keeps a small visual separation from the trigger element.
        let left, top;
        switch (pos) {
        case "top":
            left = rect.left + rect.width / 2;
            top = rect.top - baseGap;
            break;
        case "bottom":
            left = rect.left + rect.width / 2;
            top = rect.bottom + baseGap;
            break;
        case "left":
            left = rect.left - baseGap;
            top = rect.top + rect.height / 2;
            break;
        case "right":
            left = rect.right + baseGap;
            top = rect.top + rect.height / 2;
            break;
        case "top-left":
            left = rect.left;
            top = rect.top - baseGap;
            break;
        case "top-right":
            left = rect.right;
            top = rect.top - baseGap;
            break;
        case "bottom-left":
            left = rect.left;
            top = rect.bottom + baseGap;
            break;
        case "bottom-right":
            left = rect.right;
            top = rect.bottom + baseGap;
            break;
        default:
            left = rect.left; top = rect.bottom + baseGap;
        }

        // Normalize offset: x > 0 moves right, y > 0 moves down,
        // regardless of the chosen position. We apply it via an extra translate().
        const ox = offset?.x ?? 0;
        const oy = offset?.y ?? 0;

        // Final style uses (left, top) + base transform (anchor) + offset translate.
        // Using transform for offset avoids mixing layout numbers with micro-adjustments,
        // and keeps subpixel rendering smooth.
        setStylePos({
            left,
            top,
            transform: `${baseTransform} translate(${ox}px, ${oy}px)`,
        });
    }, [position, offset?.x, offset?.y]);

    const open = useCallback(() => {
        if (showTimer.current) clearTimeout(showTimer.current);
        showTimer.current = setTimeout(() => {
            computePosition();
            setIsVisible(true);
        }, delay);
    }, [delay, computePosition]);

    const close = useCallback(() => {
        if (showTimer.current) clearTimeout(showTimer.current);
        if (hideTimer.current) clearTimeout(hideTimer.current);
        hideTimer.current = setTimeout(() => setIsVisible(false), hideDelay);
    }, [hideDelay]);

    // Recompute tooltip position when the page scrolls or the window resizes.
    // This effect only runs while the tooltip is visible.
    useEffect(() => {
        if (!isVisible) return;

        // `ticking` is used as a simple rAF throttle flag
        // so that we don't call computePosition too often during continuous events.
        let ticking = false;

        const onScrollOrResize = () => {
            if (ticking) return;
            ticking = true;
            requestAnimationFrame(() => {
                computePosition(); // re-align tooltip to the trigger element
                ticking = false;
            });
        };

        // Capture phase for scroll is important: tooltips may be inside
        // scrollable containers, so we want to catch all bubbling scroll events.
        window.addEventListener("scroll", onScrollOrResize, true);
        window.addEventListener("resize", onScrollOrResize);

        // Clean up listeners when tooltip hides or component unmounts
        return () => {
            window.removeEventListener("scroll", onScrollOrResize, true);
            window.removeEventListener("resize", onScrollOrResize);
        };
    }, [isVisible, computePosition]);

    useEffect(() => {
        return () => {
            if (showTimer.current) clearTimeout(showTimer.current);
            if (hideTimer.current) clearTimeout(hideTimer.current);
        };
    }, []);

    const onKeyDown = (e) => {
        if (e.key === "Escape") close();
    };

    return (
        <div
            className={styles.tooltipContainer}
            onMouseEnter={open}
            onMouseLeave={close}
            onFocus={open}
            onBlur={close}
            onKeyDown={onKeyDown}
            aria-describedby={tooltipId}
            ref={triggerRef}
            tabIndex={0}
        >
            {children}
            {ReactDOM.createPortal(
                <div
                    id={tooltipId}
                    ref={tooltipRef}
                    role="tooltip"
                    aria-hidden={!isVisible}
                    className={cx(styles.tooltipBox, isVisible && styles.tooltipBoxVisible, className)}
                    style={stylePos}
                >
                    {text}
                </div>,
                document.body
            )}
        </div>
    );
};

Tooltip.propTypes = {
    children: PropTypes.node.isRequired,
    text: PropTypes.string,
    delay: PropTypes.number,
    hideDelay: PropTypes.number,
    className: PropTypes.string,
    position: PropTypes.oneOf([
        "top",
        "bottom",
        "left",
        "right",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ]),
    offset: PropTypes.shape({
        x: PropTypes.number,
        y: PropTypes.number,
    }),
};

export default Tooltip;
