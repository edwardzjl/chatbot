import styles from "./index.module.css";

import { useRouteError, useNavigate } from "react-router-dom";


const ErrorPage = () => {
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
            {/* Yes, `&apos;` is html5 only. But I feel `&lsquo;` and `&rsquo;` weird as there's no left or right in single quote. */}
            <p className={styles.message}>Sorry, we couldn&apos;t find the page you are looking for...</p>
            <button className={styles.homeButton} onClick={handleClick}>
                HOME
            </button>
        </div>
    );
}

export default ErrorPage;
