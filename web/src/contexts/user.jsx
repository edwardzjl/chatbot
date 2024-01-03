import { createContext, useEffect, useState } from "react";
import generateName from "names";


export const UserContext = createContext({
    userid: generateName(),
    username: generateName(),
    email: generateName(),
});

export const UserProvider = ({ children }) => {
    const [userid, setUserid] = useState("");
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");

    useEffect(() => {
        const initialization = async () => {
            const res = await fetch("/api/userinfo");
            if (res.ok) {
                const data = await res.json();
                if (data.userid) {
                    setUserid(data.userid);
                }
                if (data.username) {
                    setUsername(data.username);
                }
                if (data.email) {
                    setEmail(data.email);
                }
            } else {
                console.error("error getting userinfo", res);
            }
        };
        initialization();

        return () => { };
    }, []);

    return (
        <UserContext.Provider value={{ userid, username, email }}>
            {children}
        </UserContext.Provider>
    );
}
