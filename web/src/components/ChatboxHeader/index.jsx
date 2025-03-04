import styles from "./index.module.css";

import ThemeSelector from "@/components/ThemeSelector";
import UserMenu from "@/components/UserMenu";


const ChatboxHeader = () => {
    return (
        <div className={styles.chatboxHeader}>
            <div className={styles.rightElems}>
                <ThemeSelector />
                <UserMenu />
            </div>
        </div>
    );
};

export default ChatboxHeader;
