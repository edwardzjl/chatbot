import styles from "./index.module.css";

import { createContext, memo, useCallback, useContext, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";


/**
 * Context providing state and actions for managing dropdown open/close behavior.
 * @type {React.Context<{ open: boolean; setOpen: (open: boolean) => void }>}
 */
const DropdownContext = createContext({
    open: false,
    setOpen: () => { },
});


/**
 * A container component for creating a dropdown menu. Manages the open/close state and handles closing when clicking outside.
 *
 * @component
 * @param {Object} props - The props for the Dropdown component.
 * @param {React.ReactNode} props.children - The child elements to render within the dropdown.
 * @param {string} [props.className] - Additional CSS class names to apply to the dropdown container.
 * @returns {JSX.Element} The rendered dropdown container.
 */
export const Dropdown = ({ children, className, ...props }) => {
    const [open, setOpen] = useState(false);
    const dropdownRef = useRef(null);

    const close = useCallback((e) => {
        if (!dropdownRef.current.contains(e.target)) {
            setOpen(false);
        }
    }, []);

    useEffect(() => {
        if (open) {
            window.addEventListener("click", close);
        }

        return () => {
            window.removeEventListener("click", close);
        };
    }, [open, close]);

    return (
        <DropdownContext.Provider value={{ open, setOpen }}>
            <div className={`${styles.dropdown} ${className}`} ref={dropdownRef} {...props}>
                {children}
            </div>
        </DropdownContext.Provider>
    );
};

Dropdown.propTypes = {
    children: PropTypes.node.isRequired,
    className: PropTypes.string,
};

export const DropdownIndicator = memo(({ className }) => {
    const { open } = useContext(DropdownContext);

    return (
        <span className={`${styles.dropdownIndicator} ${open ? styles.open : ""} ${className}`}>
            ▼
        </span>
    );
});
DropdownIndicator.displayName = "DropdownIndicator";
DropdownIndicator.propTypes = {
    className: PropTypes.string,
};


/**
 * A button component to toggle the open/close state of the dropdown.
 *
 * @component
 * @param {Object} props - The props for the DropdownButton component.
 * @param {React.ReactNode} props.children - The content to display inside the button.
 * @param {string} [props.className] - Additional CSS class names to apply to the button.
 * @returns {JSX.Element} The rendered dropdown button.
 */
export const DropdownButton = ({ children, className, ref, ...props }) => {
    const { open, setOpen } = useContext(DropdownContext);

    const toggleOpen = useCallback((e) => {
        // if I `stopPropagation` here other DropdownMenu will not be closed when click on this.
        // e.stopPropagation();
        // However, `preventDefault` works, which is quite unintuitive.
        e.preventDefault();
        setOpen(prevOpen => !prevOpen);
    }, [setOpen]);

    return (
        <button
            ref={ref} // Attach ref to button
            className={`${styles.dropdownButton} ${className}`}
            onClick={toggleOpen}
            aria-expanded={open}
            {...props}
        >
            {children}
        </button>
    );
};

DropdownButton.propTypes = {
    children: PropTypes.node.isRequired,
    className: PropTypes.string,
    ref: PropTypes.oneOfType([PropTypes.func, PropTypes.shape({ current: PropTypes.instanceOf(Element) })]),
};

/**
 * A menu component for displaying dropdown items. Automatically hides when the dropdown is closed.
 *
 * @component
 * @param {Object} props - The props for the DropdownMenu component.
 * @param {React.ReactNode} props.children - The content to display inside the dropdown menu.
 * @param {string} [props.className] - Additional CSS class names to apply to the menu.
 * @returns {JSX.Element} The rendered dropdown menu.
 */
export const DropdownMenu = ({ children, className, buttonRef, ...props }) => {
    const { open, setOpen } = useContext(DropdownContext);
    const dropdownRef = useRef(null);
    const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0 });
    const [isPositionCalculated, setIsPositionCalculated] = useState(false);

    useEffect(() => {
        if (!buttonRef?.current) {
            // if buttonRef is not provided, or does not exists, do not calculate position
            setIsPositionCalculated(true);
            return;
        }
        if (!open) {
            // reset position when dropdown is closed
            setIsPositionCalculated(false);
            return;
        }

        const rect = buttonRef.current.getBoundingClientRect();

        let leftAnchor = rect.right;
        let topAnchor = rect.bottom;

        if (dropdownRef.current) {
            const viewportWidth = window.innerWidth;
            const menuWidth = dropdownRef.current.offsetWidth;
            leftAnchor = Math.min(leftAnchor, viewportWidth - menuWidth);
            leftAnchor = Math.max(leftAnchor, 0);

            const viewportHeight = window.innerHeight;
            const menuHeight = dropdownRef.current.offsetHeight;
            topAnchor = Math.min(topAnchor, viewportHeight - menuHeight);
            topAnchor = Math.max(topAnchor, 0);
        }

        setMenuPosition({
            top: topAnchor,
            left: leftAnchor,
        });
        setIsPositionCalculated(true);
    }, [open, buttonRef]);

    const menuStyle = buttonRef?.current ? { top: menuPosition.top, left: menuPosition.left } : {};
    const dropdownMenuClassName = `${styles.dropdownMenu} ${!open && styles.hidden} ${className} ${isPositionCalculated ? styles.visible : ''}`;

    return (
        <menu
            ref={dropdownRef}
            className={dropdownMenuClassName}
            onClick={() => setOpen(false)}
            aria-hidden={!open}
            role="menu"
            style={menuStyle}
            {...props}
        >
            {children}
        </menu>
    );
};

DropdownMenu.propTypes = {
    children: PropTypes.node.isRequired,
    className: PropTypes.string,
    buttonRef: PropTypes.oneOfType([PropTypes.func, PropTypes.shape({ current: PropTypes.instanceOf(Element) })]),
};
