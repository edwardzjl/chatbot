import "./index.css";

import ThemeToggle from "components/ThemeToggle";


const ChatBoxHeader = () => {

    return (
        <div className="chatbox-header">
            <ThemeToggle />
        </div>
    );
};

export default ChatBoxHeader;
