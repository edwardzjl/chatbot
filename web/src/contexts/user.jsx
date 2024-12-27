import { createContext, useEffect, useState } from "react";
import sha256 from "js-sha256";

import generateName from "@/names";

export const UserContext = createContext({
    userid: generateName(),
    username: generateName(),
    email: "",
    avatar: "https://www.gravatar.com/avatar/?d=identicon",
});

export const UserProvider = ({ children }) => {
    const [userid, setUserid] = useState("");
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [avatar, setAvatar] = useState("https://www.gravatar.com/avatar/?d=identicon");

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

    useEffect(() => {
        const getGravatarURL = (email) => {
            // Trim leading and trailing whitespace from an email address and force all characters to lower case
            const address = String(email).trim().toLowerCase();

            // Create a SHA256 hash of the final string
            const hash = sha256(address);

            // Grab the actual image URL
            return `https://www.gravatar.com/avatar/${hash}/?d=identicon`;
        };

        if (email !== "") {
            setAvatar(getGravatarURL(email));
        }
    }, [email]);

    return (
        <UserContext.Provider value={{ userid, username, email, avatar }}>
            {children}
        </UserContext.Provider>
    );
}
