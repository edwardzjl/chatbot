import { useEffect, useReducer } from "react";
import PropTypes from "prop-types";

import { ConversationContext } from "./index";
import { conversationReducer } from "./reducer";


export const ConversationProvider = ({ children }) => {

    // It seems that I can't use async function as the `init` param.
    // So I opt to use `useEffect` instead.
    const [groupedConvsArray, dispatch] = useReducer(
        conversationReducer,
        [],
    );

    useEffect(() => {
        const init = async () => {
            const convs = await fetch("/api/conversations", {
            }).then((res) => res.json());

            dispatch({
                type: "replaceAll",
                convs: convs
            });
        };

        init();
    }, []);

    return (
        <ConversationContext.Provider value={{ groupedConvsArray, dispatch }}>
            {children}
        </ConversationContext.Provider>
    );
};

ConversationProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
