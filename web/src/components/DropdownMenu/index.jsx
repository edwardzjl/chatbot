import styles from "./index.module.css";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";

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

/**
 * A button component to toggle the open/close state of the dropdown.
 *
 * @component
 * @param {Object} props - The props for the DropdownButton component.
 * @param {React.ReactNode} props.children - The content to display inside the button.
 * @param {string} [props.className] - Additional CSS class names to apply to the button.
 * @returns {JSX.Element} The rendered dropdown button.
 */
export const DropdownButton = ({ children, className, ...props }) => {
    const { open, setOpen } = useContext(DropdownContext);

    const toggleOpen = useCallback(() => {
        // if I stop propagation here the DropdownMenu will not be closed when click on another dropdown menu.
        // e.stopPropagation();
        setOpen(!open);
    }, [open, setOpen]);

    return (
        <button
            className={`${styles.dropdownButton} ${className}`}
            onClick={toggleOpen}
            aria-expanded={open}
            {...props}
        >
            {children}
        </button>
    );
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
export const DropdownMenu = ({ children, className, ...props }) => {
    const { open, setOpen } = useContext(DropdownContext);

    return (
        <menu
            className={`${styles.dropdownMenu} ${!open && styles.hidden} ${className}`}
            onClick={() => setOpen(false)}
            aria-hidden={!open}
            role="menu"
            {...props}
        >
            {children}
        </menu>
    );
};
