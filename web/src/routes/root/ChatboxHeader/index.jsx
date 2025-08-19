import styles from "./index.module.css";

import ThemeSelector from "@/components/ThemeSelector";

import ModelSelector from "./ModelSelector";
import UserMenu from "./UserMenu";

const ChatboxHeader = () => {
    return (
        <header className={styles.chatboxHeader}>
            <ModelSelector />
            <div className={styles.rightElems}>
                <ThemeSelector />
                <UserMenu />
            </div>
        </header>
    );
};

export default ChatboxHeader;
