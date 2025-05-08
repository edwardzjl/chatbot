import styles from "./index.module.css";

import { useContext } from "react";

import { ConfigContext } from "@/contexts/config";

import { Dropdown, DropdownButton, DropdownMenu, DropdownIndicator } from "@/components/DropdownMenu";


const ModelSelector = () => {
    const { models, selectedModel, setSelectedModel } = useContext(ConfigContext);

    return (
        <Dropdown>
            <DropdownButton className={styles.title}>
                <span className={styles.titleText}>{selectedModel}</span>
                <DropdownIndicator className={styles.dropdownIndicator} />
            </DropdownButton>
            <DropdownMenu className={styles.menuList}>
                {models.map((model, index) => (
                    <li key={index}>
                        <button
                            className={`${styles.menuItem} ${model.name === selectedModel && styles.selected}`}
                            onClick={() => setSelectedModel(model.name)}
                            aria-label={`Select ${model.name}`}
                        >
                            <span className={styles.menuItemTitle}>{model.name}</span>
                        </button>
                    </li>
                ))}
            </DropdownMenu>
        </Dropdown>
    );
};

export default ModelSelector;
