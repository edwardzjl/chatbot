import "./index.css";

import { useEffect } from "react";
import { useLoaderData, redirect } from "react-router-dom";

import ChatboxHeader from "components/ChatboxHeader";

import ChatLog from "../conversation/ChatLog";
import ChatMessage from "../conversation/ChatMessage";

export async function loader({ params }) {
    const resp = await fetch(`/api/shares/${params.shareId}`, {});
    if (!resp.ok) {
        console.error("Failed to fetch share");
        return redirect("/");
    }
    const share = await resp.json();
    console.log('data', share);
    return { share };
}

const Share = () => {
    const { share } = useLoaderData();

    useEffect(() => {
        console.log('share', share);
    }
    , [share]);
    return (
        <>
            <ChatboxHeader />
            <ChatLog className="chat-log">
                {share?.messages?.map((message, index) => (
                    <ChatMessage key={index} convId={share.id} idx={index} message={message} />
                ))}
            </ChatLog>
        </>
    );
};

export default Share;
