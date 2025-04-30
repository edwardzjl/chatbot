import { useEffect, useState } from "react";
import PropTypes from "prop-types";

import { PreferenceContext } from "./index";


const getPreference = () => {
    const preference = localStorage.getItem("preference");
    if (preference) {
        return  JSON.parse(preference);
    }
    return {
        forceThinking: false,
    };
};

export const PreferenceProvider = ({ children }) => {
    const [preference, setPreference] = useState(getPreference());

    // Flush the preference to localStorage
    useEffect(() => {
        localStorage.setItem("preference", JSON.stringify(preference));
    }, [preference]);

    return (
        <PreferenceContext.Provider value={{ preference, setPreference }}>
            {children}
        </PreferenceContext.Provider>
    );
};

PreferenceProvider.propTypes = {
    children: PropTypes.node.isRequired,
};
