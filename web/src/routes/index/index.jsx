import styles from './index.module.css';

import { useContext } from "react";
import { useNavigate } from "react-router-dom";

import { UserContext } from "@/contexts/user";
import { ConversationContext } from "@/contexts/conversation";
import ChatboxHeader from "@/components/ChatboxHeader";
import { toLocalISOString, DEFAULT_CONV_TITLE } from "@/commons";

import ChatInput from "./ChatInput";


const Conversation = () => {
    const { username } = useContext(UserContext);
    const { dispatch } = useContext(ConversationContext);
    const navigate = useNavigate();

    const handleSubmit = async (input) => {
        try {
            const response = await fetch("/api/conversations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ title: DEFAULT_CONV_TITLE }),
            });
            const conversation = await response.json();
            const sent_at = toLocalISOString(new Date());
            const message = {
                id: crypto.randomUUID(),
                conversation: conversation.id,
                from: username,
                content: input,
                type: "human",
                sent_at: sent_at,
            };
            sessionStorage.setItem(`init-msg:${conversation.id}`, JSON.stringify(message));
            dispatch({ type: "added", conv: conversation });
            navigate(`/conversations/${conversation.id}`);
        } catch (error) {
            console.error('Error creating conversation:', error);
        }
    };

    return (
        <section className={styles.chatbox}>
            <ChatboxHeader />
            <div className={styles.welcomeContainer}>
                <div className={styles.welcome}>{username ? `${username}, hello!` : "Hello!"}</div >
                <div className={styles.welcome}>How can I help you today?</div >
            </div>
            {/* TODO: add some examples here? */}
            <div className={styles.inputBottom}>
                <ChatInput onSubmit={handleSubmit} />
                <div className={styles.footer}>Chatbot can make mistakes. Consider checking important information.</div>
            </div>
        </section>
    );
}

export default Conversation;
