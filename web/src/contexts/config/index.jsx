import { createContext } from "react";


export const ConfigContext = createContext({
    models: [],
    selectedModel: null,
    setSelectedModel: () => { },
});
