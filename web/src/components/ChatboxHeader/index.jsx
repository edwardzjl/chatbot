import styles from "./index.module.css";

import ThemeSelector from "@/components/ThemeSelector";
import UserMenu from "@/components/UserMenu";

import ModelSelector from "./ModelSelector";

const ChatboxHeader = () => {
    return (
        <div className={styles.chatboxHeader}>
            <ModelSelector />
            <div className={styles.rightElems}>
                <ThemeSelector />
                <UserMenu />
            </div>
        </div>
    );
};

export default ChatboxHeader;
