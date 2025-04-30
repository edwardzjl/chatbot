import { createContext } from "react";


export const PreferenceContext = createContext({
    preference: {
        forceThinking: false,
    },
    setPreference: () => { },
});
