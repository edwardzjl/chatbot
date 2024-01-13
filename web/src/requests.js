
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
 * Generate a summarization of the conversation.
 * @param {string} conversationId 
 * @returns {object} {summary: string}
 */
export const summarizeConversation = async (conversationId) => {
    return fetch(`/api/conversations/${conversationId}/summarization`, {
        method: "POST",
    }).then(res => res.json());
}
