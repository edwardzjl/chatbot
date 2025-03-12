import { useEffect, useReducer } from "react";
import PropTypes from "prop-types";

import { ConversationContext } from "./index";
import { conversationReducer, groupConvs } from "./reducer";


export const ConversationProvider = ({ children }) => {

    // It seems that I can't use async function as the `init` param.
    // So I opt to use `useEffect` instead.
    const [groupedConvs, dispatch] = useReducer(
        conversationReducer,
        {},
    );

    useEffect(() => {
        const init = async () => {
            const convs = await fetch("/api/conversations", {
            }).then((res) => res.json());

            // This assumes that the convs are already sorted by the server.
            // Otherwise, I need to call `sortConvs` first.
            const groupedConvs = groupConvs(convs);

            dispatch({
                type: "replaceAll",
                groupedConvs
            });
        };

        init();
    }, []);

    return (
        <ConversationContext.Provider value={{ groupedConvs, dispatch }}>
            {children}
        </ConversationContext.Provider>
    );
};

ConversationProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
