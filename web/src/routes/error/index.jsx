import "./index.css";

import { useRouteError, useNavigate } from "react-router-dom";

export default function ErrorPage() {
    const navigate = useNavigate();

    const error = useRouteError();
    console.error(error);

    const handleClick = () => {
        navigate("/");
    }

    return (
        <div id="error-page" className="container">
            <h1><span>{error.status} {error.statusText || error.message}</span></h1>
            <h2>Oops!</h2>
            <p>The page you are looking for does not exist. You can click the button below to go back to the homepage.</p>
            <button onClick={handleClick}>HOME</button>
        </div>
    );
}
