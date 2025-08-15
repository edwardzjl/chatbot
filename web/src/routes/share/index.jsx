import styles from "./index.module.css";

import { useLoaderData, redirect } from "react-router";

import ChatLog from "@/components/ChatLog";
import ChatMessage from "@/components/ChatMessage";

import { formatTimestamp } from "@/commons";

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
    const rendering_messages = new Set(["human", "ai"]);

    const goHome = () => {
        // As the share page is public, I need to refresh the page to perform login when redirecting to the home page.
        // This is why window.location is used instead of useNavigate.
        window.location.href = "/";
    }

    return (
        <div className={styles.App}>
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
