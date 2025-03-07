import styles from './index.module.css';

import { useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { loadPyodide } from "pyodide";

import { UserContext } from "@/contexts/user";
import { ConversationContext } from "@/contexts/conversation";
import ChatboxHeader from "@/components/ChatboxHeader";
import { DEFAULT_CONV_TITLE } from "@/commons";

import ChatInput from "./ChatInput";


const Conversation = () => {
    const { username } = useContext(UserContext);
    const { dispatch } = useContext(ConversationContext);
    const navigate = useNavigate();

    useEffect(() => {
        const initPyodide = async () => {
            const pyodide = await loadPyodide({
                indexURL: "https://cdn.jsdelivr.net/pyodide/v0.27.3/full",
            });
            // See <https://pyodide.org/en/stable/usage/file-system.html>
            // <https://developer.mozilla.org/en-US/docs/Web/API/StorageManager/getDirectory>
            // <https://developer.mozilla.org/en-US/docs/Web/API/File_System_API/Origin_private_file_system>
            // quota: <https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria>
            const dirHandle = await navigator.storage.getDirectory();
            const permissionStatus = await dirHandle.requestPermission({
                mode: "readwrite",
            });
            if (permissionStatus !== "granted") {
                throw new Error("readwrite access to directory not granted");
            }
            // See <https://pyodide.org/en/stable/usage/api/js-api.html#pyodide.mountNativeFS>
            const nativefs = await pyodide.mountNativeFS("/mount_dir", dirHandle);
            try {
                // await pyodide.runPythonAsync(`print("hello noob)`)
                await pyodide.runPythonAsync(`1 / 0`)
            } catch (error) {
                // console.log("type of error", typeof error);  // object
                // console.log("error keys", Object.keys(error));  // 'type', '__error_address'
                console.log("error type", error.type);  //
                // console.log("error address", error.__error_address);  // 0
                // console.error("Error", error);
                console.dir(error);
            }
            // const res = await pyodide.runPythonAsync("1+1");
            // console.log("res", res);
            await nativefs.syncfs();
        }

        initPyodide();
    }, []);

    const handleSubmit = async (input) => {
        try {
            const response = await fetch("/api/conversations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ title: DEFAULT_CONV_TITLE }),
            });
            const conversation = await response.json();
            const message = {
                id: crypto.randomUUID(),
                conversation: conversation.id,
                from: username,
                content: input,
                type: "human",
            };
            sessionStorage.setItem(`init-msg:${conversation.id}`, JSON.stringify(message));
            dispatch({ type: "added", conv: conversation });
            navigate(`/conversations/${conversation.id}`);
        } catch (error) {
            console.error('Error creating conversation:', error);
        }
    };

    return (
        <section className={styles.chatbox}>
            <ChatboxHeader />
            <div className={styles.welcomeContainer}>
                <div className={styles.welcome}>{username ? `${username}, hello!` : "Hello!"}</div >
                <div className={styles.welcome}>How can I help you today?</div >
            </div>
            {/* TODO: add some examples here? */}
            <div className={styles.inputBottom}>
                <ChatInput onSubmit={handleSubmit} />
                <div className={styles.footer}>Chatbot can make mistakes. Consider checking important information.</div>
            </div>
        </section>
    );
}

export default Conversation;
