import styles from "./index.module.css";

import { useContext } from "react";
import { useLoaderData, redirect } from "react-router-dom";

import ChatLog from "@/components/ChatLog";
import ChatMessage from "@/components/ChatMessage";
import { ThemeContext } from "@/contexts/theme";


async function loader({ params }) {
    const resp = await fetch(`/api/shares/${params.shareId}`, {});
    if (!resp.ok) {
        console.error("Failed to fetch share");
        return redirect("/");
    }
    const share = await resp.json();
    return { share };
}

const Share = () => {
    const { share } = useLoaderData();
    const { theme } = useContext(ThemeContext);
    const rendering_messages = new Set(["human", "ai"]);

    const goHome = () => {
        // As the share page is public, I need to refresh the page to perform login when redirecting to the home page.
        // This is why window.location is used instead of useNavigate.
        window.location.href = "/";
    }

    const formatTimestamp = (timestamp) => {
        const ts = new Date(timestamp);
        const userLocale = navigator.language || "en-US"; // Fallback to "en-US" if not available

        return ts.toLocaleString(userLocale, {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        });
    }


    return (
        <div className={`${styles.App} theme-${theme}`}>
            <div className={styles.sharebox}>
                <div className={styles.shareHeader}>
                    <h1 className={styles.shareTitle}>{share.title}</h1>
                    <p>Shared @ {formatTimestamp(share.created_at)}</p>
                </div>
                <ChatLog className={styles.chatLog}>
                    {share?.messages?.filter(message => rendering_messages.has(message.type)).map((message, index) => (
                        <ChatMessage key={index} convId={share.id} idx={index} message={message} />
                    ))}
                </ChatLog>
                <button className={styles.shartButton} onClick={goHome} aria-label="Start chatting">Start chatting!</button>
            </div>
        </div>
    );
};

export default Share;
Share.loader = loader;
