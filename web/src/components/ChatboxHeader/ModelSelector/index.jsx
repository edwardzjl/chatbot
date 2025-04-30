import styles from "./index.module.css";

import { useContext } from "react";

import { PreferenceContext } from "@/contexts/preference";
import { Dropdown, DropdownButton, DropdownMenu } from "@/components/DropdownMenu";


const ModelSelector = () => {
    const { preference, setPreference } = useContext(PreferenceContext);

    return (
        <Dropdown>
            <DropdownButton className={styles.title}>
                <span className={styles.titleText}>{preference.forceThinking === false ? "Flash" : "Pro"}</span>
            </DropdownButton>
            <DropdownMenu className={styles.menuList}>
                <li>
                    <button
                        className={`${styles.menuItem} ${preference.forceThinking === false && styles.selected}`}
                        onClick={() => setPreference({
                            forceThinking: false,
                        })}
                        aria-label="Set response mode to flash"
                    >
                        <span className={styles.menuItemTitle}>Flash</span>
                        <span className={styles.menuItemText}>Best for everyday conversations.</span>
                    </button>
                </li>
                <li>
                    <button
                        className={`${styles.menuItem} ${preference.forceThinking === true && styles.selected}`}
                        onClick={() => setPreference({
                            forceThinking: true,
                        })}
                        aria-label="Set response mode to pro"
                    >
                        <span className={styles.menuItemTitle}>Pro</span>
                        <span className={styles.menuItemText}>Ideal for deep or serious questions.</span>
                    </button>
                </li>
            </DropdownMenu>
        </Dropdown>
    );
};

export default ModelSelector;
