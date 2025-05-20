import { useContext } from "react";

import { UserContext } from "./index";

export const useUserProfile = () => {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error("useUserProfile must be used within a UserProvider");
    }
    return context;
};
