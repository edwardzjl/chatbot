import "./index.css";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";

const DropdownContext = createContext({
    open: false,
    setOpen: () => { },
});

export const DropdownMenu = ({ children, className, ...props }) => {
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
            <div className={className} ref={dropdownRef} {...props}>{children}</div>
        </DropdownContext.Provider>
    );
};

export const DropdownHeader = ({ children, className, ...props }) => {
    const { open, setOpen } = useContext(DropdownContext);

    const toggleOpen = useCallback(() => {
        // if I stop propagation here the dropdown list will not be closed when click on another dropdown menu.
        // e.stopPropagation();
        setOpen(!open);
    }, [open, setOpen]);

    return (
        <button className={className} onClick={toggleOpen} {...props}>
            {children}
        </button>
    );
};

export const DropdownList = ({ children, className, ...props }) => {
    const { open, setOpen } = useContext(DropdownContext);

    return (
        <menu className={`dropdown-list ${!open && "hidden"} ${className}`} onClick={() => setOpen(false)} {...props}>
            {children}
        </menu>
    );
};
