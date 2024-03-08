import "./index.css";

import { useContext } from "react";

import { UserContext } from "contexts/user";
import ChatboxHeader from "components/ChatboxHeader";

import ChatInput from "./ChatInput";


const Conversation = () => {
    const { username } = useContext(UserContext);
    return (
        <>
            <ChatboxHeader />
            <div className="welcome-container">
                <div className="welcome">{username}, hello!</div >
                <div className="welcome">How can I help you today?</div >
            </div>
            {/* TODO: add some examples here? */}
            <div className="input-bottom">
                <ChatInput />
                <div className="footer">Chatbot can make mistakes. Consider checking important information.</div>
            </div>
        </>
    );
}

export default Conversation;
