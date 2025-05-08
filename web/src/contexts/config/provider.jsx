import { useCallback, useEffect, useState } from "react";
import PropTypes from "prop-types";

import { ConfigContext } from "./index";


const SESSION_STORAGE_MODELS_KEY = "appConfigModels";
const LOCAL_STORAGE_SELECTED_MODEL_KEY = "appConfigSelectedModel";


export const ConfigProvider = ({ children }) => {
    const [models, setModels] = useState([]);
    // The `_setSelectedModel` is a private setter to avoid exposing it directly,
    // because we need to check if the selected model is valid in the models list
    const [selectedModel, _setSelectedModel] = useState(null);

    const setSelectedModel = useCallback((modelName) => {
        const modelToSelect = models.find(model => model.name === modelName);

        if (modelToSelect) {
            _setSelectedModel(modelName);
        } else {
            console.warn(`Attempted to select model "${modelName}" but it was not found in the models list. Default to the first model.`);
            _setSelectedModel(models[0]?.name || null);
        }
        // Persist the selection
        try {
            localStorage.setItem(LOCAL_STORAGE_SELECTED_MODEL_KEY, modelName);
            console.info("Selected model stored in localStorage:", modelName);
        } catch (storageError) {
            console.error("Failed to store selected model ID in localStorage:", storageError);
        }
    }, [models]);

    // Restore models and selected model from storage on component mount.
    useEffect(() => {
        const loadConfig = async () => {
            const cachedSelectedModel = localStorage.getItem(LOCAL_STORAGE_SELECTED_MODEL_KEY);
            if (cachedSelectedModel) {
                _setSelectedModel(cachedSelectedModel);
            }

            const cachedModels = sessionStorage.getItem(SESSION_STORAGE_MODELS_KEY);
            if (cachedModels) {
                try {
                    const data = JSON.parse(cachedModels);
                    setModels(data);
                    console.info("Loaded models from sessionStorage");
                    // !NOTE: early return here.
                    return;
                } catch (parseError) {
                    console.error("Failed to parse models from sessionStorage, fetching...", parseError);
                }
            }
            console.info("Models not found in sessionStorage or parsing failed, fetching...");
            try {
                const res = await fetch("/api/models");
                if (res.ok) {
                    const data = await res.json();
                    setModels(data);
                    try {
                        sessionStorage.setItem(SESSION_STORAGE_MODELS_KEY, JSON.stringify(data));
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
    }, []);

    // Check/Update Selected Model when `models` Change
    useEffect(() => {
        if (!models || models.length === 0) {
            return;
        }

        console.info("Models list updated, checking selected model validity...");
        const foundModel = models.find(model => model.name === selectedModel);
        if (foundModel) {
            // selected model is still valid
            return;
        }

        console.warn(`Current selected model name "${selectedModel}" is not in the updated models list. Updating selection.`);
        const newSelectedModelName = models[0].name;

        // *** Update the state ***
        _setSelectedModel(newSelectedModelName);

        // *** Update localStorage ***
        try {
            localStorage.setItem(LOCAL_STORAGE_SELECTED_MODEL_KEY, newSelectedModelName);
            console.info("Updated selected model name stored in localStorage:", newSelectedModelName);
        } catch (storageError) {
            console.error("Failed to store updated selected model name in localStorage:", storageError);
        }
    }, [models, selectedModel]);


    return (
        <ConfigContext.Provider value={{ models, selectedModel, setSelectedModel }}>
            {children}
        </ConfigContext.Provider>
    );
};

ConfigProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
