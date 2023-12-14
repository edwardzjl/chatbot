import "./index.css";

import { createContext, useContext, useEffect, useRef, useState } from "react";

const DropdownContext = createContext({
    open: false,
    setOpen: () => { },
});

export const DropdownMenu = ({ children, ...props }) => {
    const [open, setOpen] = useState(false);
    const dropdownRef = useRef(null);

    useEffect(() => {
        const close = (e) => {
            if (!dropdownRef.current.contains(e.target)) {
                setOpen(false);
            }
        };
        if (open) {
            window.addEventListener("click", close);
        }

        return () => {
            window.removeEventListener("click", close);
        };
    }, [open]);

    return (
        <DropdownContext.Provider value={{ open, setOpen }}>
            <div ref={dropdownRef} {...props}>{children}</div>
        </DropdownContext.Provider>
    );
};

export const DropdownHeader = ({ children, ...props }) => {
    const { open, setOpen } = useContext(DropdownContext);

    const toggleOpen = () => {
        setOpen(!open);
    };

    return (
        <button onClick={toggleOpen} {...props}>
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
