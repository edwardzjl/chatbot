import styles from './index.module.css';

import { useNavigate } from "react-router-dom";

import ChatboxHeader from "@/components/ChatboxHeader";
import ChatInput from "@/components/ChatInput";

import { useUserProfile } from "@/contexts/user/hook";
import { useConversations } from "@/contexts/conversation/hook";

import { DEFAULT_CONV_TITLE } from "@/commons";


const Conversation = () => {
    const { username } = useUserProfile();
    const { dispatch } = useConversations();
    const navigate = useNavigate();

    const handleSubmit = async (message) => {
        const response = await fetch("/api/conversations", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title: DEFAULT_CONV_TITLE }),
        });
        const conversation = await response.json();
        const payload = {
            conversation: conversation.id,
            from: username,
            ...message,
        };
        sessionStorage.setItem(`init-msg:${conversation.id}`, JSON.stringify(payload));
        dispatch({ type: "added", conv: conversation });
        navigate(`/conversations/${conversation.id}`);
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
