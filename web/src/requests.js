/**
 * Create a conversation
 * @returns 
 */
export const createConversation = async () => {
    return fetch("/api/conversations", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
    }).then((res) => res.json());
};

/**
 * Get all conversations of the user. These conversations are conversation overviews that does not contain messages.
 * To get a conversation with messages, use getConversation.
 * @returns 
 */
export const getConversations = async () => {
    return fetch("/api/conversations", {
    }).then((res) => res.json())
}

/**
 * Get a conversation by id. This conversation will contain messages.
 * @param {string} conversationId 
 * @returns 
 */
export const getConversation = async (conversationId) => {
    return fetch(`/api/conversations/${conversationId}`, {
    }).then((res) => res.json());
}

/**
 * Delete a conversation
 * @param {string} conversationId 
 */
export const deleteConversation = async (conversationId) => {
    return fetch(`/api/conversations/${conversationId}`, {
        method: "DELETE",
    })
};

/**
 * Update a conversation. Only supports update the conversation title.
 * @param {string} conversationId 
 * @param {string} title
 */
export const updateConversation = async (conversationId, title) => {
    return fetch(`/api/conversations/${conversationId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            title: title,
        }),
    })
};
