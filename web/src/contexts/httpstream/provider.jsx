import { useCallback, useRef } from "react";
import PropTypes from "prop-types";

import { HttpStreamContext } from "./index";


export const HttpStreamProvider = ({ children }) => {
    const messageHandlers = useRef([]);

    const send = useCallback(async (url, message) => {
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(message),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.trim().startsWith('data: ')) {
                        const data = line.trim().substring(6); // Remove 'data: '
                        if (data) {
                            // Call all registered message handlers
                            messageHandlers.current.forEach(handler => {
                                try {
                                    handler(data);
                                } catch (error) {
                                    console.error("Error in message handler", error);
                                }
                            });
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Error in HTTP stream:", error);
            
            // Send error message to handlers
            const errorMessage = JSON.stringify({
                type: "error",
                content: "Connection error occurred"
            });
            
            messageHandlers.current.forEach(handler => {
                try {
                    handler(errorMessage);
                } catch (handlerError) {
                    console.error("Error in error message handler", handlerError);
                }
            });
        }
    }, []);

    const registerMessageHandler = useCallback((handler) => {
        messageHandlers.current.push(handler);
        return handler; // Return for unregistration reference
    }, []);

    const unregisterMessageHandler = useCallback((handler) => {
        messageHandlers.current = messageHandlers.current.filter(h => h !== handler);
    }, []);

    return (
        <HttpStreamContext.Provider
            value={{
                send,
                registerMessageHandler,
                unregisterMessageHandler,
            }}
        >
            {children}
        </HttpStreamContext.Provider>
    )
};

HttpStreamProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
