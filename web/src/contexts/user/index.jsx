import { createContext } from "react";

import generateName from "@/names";


export const UserContext = createContext({
    userid: generateName(),
    username: generateName(),
    email: "",
    avatar: "https://www.gravatar.com/avatar/?d=identicon",
});
