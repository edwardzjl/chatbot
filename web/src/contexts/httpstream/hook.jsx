import { useContext } from "react";

import { HttpStreamContext } from "./index";

export const useHttpStream = () => {
    const context = useContext(HttpStreamContext);
    if (context === undefined) {
        throw new Error("useHttpStream must be used within a HttpStreamProvider");
    }
    return context;
};