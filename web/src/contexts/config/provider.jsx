import { useEffect, useState } from "react";
import PropTypes from "prop-types";

import { ConfigContext } from "./index";


export const ConfigProvider = ({ children }) => {
    const [models, setModels] = useState([]);

    useEffect(() => {
        const initialization = async () => {
            const res = await fetch("/api/models");
            if (res.ok) {
                const data = await res.json();
                setModels(data);
            } else {
                console.error("error getting config", res);
            }
        };
        initialization();

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
