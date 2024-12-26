import styles from "./index.module.css";

import { useRouteError, useNavigate } from "react-router-dom";

export default function ErrorPage() {
    const navigate = useNavigate();
    const error = useRouteError();
    console.error(error);

    const handleClick = () => {
        navigate("/");
    };

    return (
        <div className={styles.container}>
            <h1 className={styles.errorCode}>
                <span>{error.status} {error.statusText || error.message}</span>
            </h1>
            <h2 className={styles.heading}>Oops! Something went wrong.</h2>
            <p className={styles.message}>Sorry, we couldn't find the page you are looking for...</p>
            <button className={styles.homeButton} onClick={handleClick}>
                HOME
            </button>
        </div>
    );
}
