import "./index.css";

import ChatboxHeader from "components/ChatboxHeader";

import ChatInput from "./ChatInput";


const Conversation = () => {

    return (
        <>
            <ChatboxHeader />
            {/* TODO: add some examples here */}
            <div className="input-bottom">
                <ChatInput />
                <div className="footer">Chatbot can make mistakes. Consider checking important information.</div>
            </div>
        </>
    );
}

export default Conversation;
