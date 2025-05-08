import { useEffect, useState } from "react";
import PropTypes from "prop-types";

import { ConfigContext } from "./index";


const SESSION_STORAGE_KEY = "appConfigModels";


export const ConfigProvider = ({ children }) => {
    const [models, setModels] = useState([]);

    useEffect(() => {
        const loadConfig = async () => {
            const cachedModels = sessionStorage.getItem(SESSION_STORAGE_KEY);

            if (cachedModels) {
                try {
                    const data = JSON.parse(cachedModels);
                    setModels(data);
                    console.info("Loaded models from sessionStorage");
                    return;
                } catch (parseError) {
                    console.error("Failed to parse models from sessionStorage, fetching...", parseError);
                }
            } else {
                console.info("Models not found in sessionStorage, fetching...");
            }

            try {
                const res = await fetch("/api/models");
                if (res.ok) {
                    const data = await res.json();
                    setModels(data);
                    try {
                        sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(data));
                        console.info("Fetched and stored models in sessionStorage");
                    } catch (storageError) {
                        console.error("Failed to store models in sessionStorage:", storageError);
                    }
                } else {
                    console.error("Error fetching models:", res.status, res.statusText);
                }
            } catch (fetchError) {
                console.error("Network or unexpected error fetching models:", fetchError);
            }
        };

        loadConfig();

        return () => { };
    }, []);

    return (
        <ConfigContext.Provider value={{ models }}>
            {children}
        </ConfigContext.Provider>
    );
};

ConfigProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
