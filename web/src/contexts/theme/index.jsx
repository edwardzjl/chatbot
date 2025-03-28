import { createContext } from "react";


export const ThemeContext = createContext({
    theme: "",
    codeTheme: undefined,
    setTheme: () => { },
});
