import { createContext, useEffect, useState } from "react";
import generateName from "names";


export const UserContext = createContext(generateName(), () => { });

export const UserProvider = ({ children }) => {
    const [username, setUsername] = useState("");

    useEffect(() => {
        const initialization = async () => {
            const res = await fetch("/api/userinfo");
            if (res.ok) {
                const data = await res.json();
                if (data.username) {
                    setUsername(data.username);
                }
            } else {
                console.error("error getting userinfo", res);
            }
        };
        initialization();

        return () => { };
    }, []);

    return (
        <UserContext.Provider value={[username, setUsername]}>
            {children}
        </UserContext.Provider>
    );
}
