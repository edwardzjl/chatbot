import { useCallback, useEffect, useReducer, useState } from "react";
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

    const [nextCursor, setNextCursor] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const fetchMoreConvs = useCallback(async () => {
        if (isLoading) {
            return;
        }

        setIsLoading(true);
        try {
            const queryParams = new URLSearchParams();
            queryParams.append("size", "50");

            if (nextCursor) {
                queryParams.append("cursor", nextCursor);
            }

            const response = await fetch(`/api/conversations?${queryParams.toString()}`);
            const data = await response.json();

            dispatch({
                type: "added_all",
                convs: data.items
            });

            setNextCursor(data.next_page);
        } catch (error) {
            console.error("Failed to fetch conversations:", error);
        } finally {
            setIsLoading(false);
        }
    }, [isLoading, nextCursor]);

    useEffect(() => {
        // const init = async () => {
        //     const convs = await fetch("/api/conversations", {
        //     }).then((res) => res.json());

        //     dispatch({
        //         type: "replaceAll",
        //         convs: convs
        //     });
        // };

        // init();
        fetchMoreConvs();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <ConversationContext.Provider value={{ groupedConvsArray, dispatch, isLoading, fetchMoreConvs }}>
            {children}
        </ConversationContext.Provider>
    );
};

ConversationProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
