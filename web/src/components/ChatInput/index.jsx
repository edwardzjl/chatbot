import styles from "./index.module.css";

import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router";
import PropTypes from "prop-types";
import CircularProgress from "@mui/material/CircularProgress";

import SendRoundedIcon from "@mui/icons-material/SendRounded";
import AttachFileIcon from "@mui/icons-material/AttachFile";
import HighlightOffIcon from '@mui/icons-material/HighlightOff';

import PreviewImage from "@/components/PreviewImage";

import { useConfig } from "@/contexts/config/hook";
import { useSnackbar } from "@/contexts/snackbar/hook";
import { useHttpStream } from "@/contexts/httpstream/hook";

import { toLocalISOString } from "@/commons";

import { uploadFile } from "./utils";

/**
 * ChatInput Component
 *
 * This component renders a chat input form with a dynamically resizing textarea and a submit button.
 * It integrates with a WebSocket context to disable the submit button when the WebSocket is not ready.
 * The component also focuses on the textarea when the conversation ID changes and supports keyboard
 * shortcuts for submitting the input.
 *
 * Props:
 * @param {Object} props - The props object.
 * @param {Function} props.onSubmit - Callback function to handle the submission of user input.
 *                                     Receives the message as an argument.
 *                                     Should directly throw an error if the submission fails.
 *
 * Features:
 * - Dynamically adjusts the textarea height based on its content.
 * - Autofocuses the textarea when the conversation ID (`convId`) changes.
 * - Disables the submit button when the WebSocket is not ready.
 * - Supports "Enter" key for submission unless used with Ctrl, Shift, or Alt (Shift adds a new line).
 * - Allows uploading image and video attachments.
 * - Displays upload progress for attachments.
 * - Enables canceling ongoing attachment uploads.
 *
 * Contexts:
 * - Uses the `WebsocketContext` to determine the readiness state (`ready`) of the WebSocket.
 * - Uses the `SnackbarContext` to display notification messages.
 *
 * Hooks:
 * - `useState` for managing the input text, attachments list, and upload requests.
 * - `useRef` for accessing the textarea and file input DOM nodes.
 * - `useEffect` for handling focus and dynamic height adjustments.
 *
 * Usage:
 * ```jsx
 * <ChatInput onSubmit={(message) => console.log("User input:", message)} />
 * ```
 */
const ChatInput = ({ onSubmit }) => {
    const params = useParams();
    const { ready } = useHttpStream();
    const { setSnackbar } = useSnackbar();
    const { models, selectedModel } = useConfig();

    const [input, setInput] = useState("");
    const inputRef = useRef(null);

    const attachmentsInputRef = useRef(null);
    const [attachments, setAttachments] = useState([]);
    // It seems that AbortController does not work with XMLHttpRequest.
    // XMLHttpRequest has its own abort method.
    // See <https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/abort>
    const [uploadRequests, setUploadRequests] = useState({});

    /**
     * Focus on input when convId changes.
     */
    useEffect(() => {
        if (params.convId) {
            inputRef.current.focus();
        }
    }, [params]);

    /**
     * Adjusting height of textarea.
     * Ref: <https://blog.muvon.io/frontend/creating-textarea-with-dynamic-height-react>
     */
    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.style.height = "0px";
            const { scrollHeight } = inputRef.current;
            inputRef.current.style.height = `${scrollHeight}px`
        }
    }, [inputRef, input]);

    const handleSubmit = async () => {
        const message = {
            id: crypto.randomUUID(),
            content: input,
            attachments: attachments,
            type: "human",
            sent_at: toLocalISOString(new Date()),
            additional_kwargs: { model_name: selectedModel }
        };
        try {
            await onSubmit(message);
            setInput("");
            setAttachments([]);
        } catch (error) {
            console.error("Error sending message", error);
            const errormsg = (error.name === "InvalidStateError")
                ? "Connection not ready, please try again later."
                : "An error occurred, please try again later.";
            setSnackbar({
                open: true,
                severity: "error",
                message: errormsg,
            });
        }
    };

    const handleKeyDown = async (e) => {
        // <https://developer.mozilla.org/zh-CN/docs/Web/API/Element/keydown_event>
        if (e.isComposing || e.keyCode === 229) {
            return;
        }
        if (e.key === "Enter") {
            if (e.ctrlKey || e.shiftKey || e.altKey) {
                // won't trigger submit here, but only shift key will add a new line
                return true;
            }
            e.preventDefault();
            await handleSubmit(e);
        }
    };

    const handleUploadButtonClick = (e) => {
        e.preventDefault();
        attachmentsInputRef.current.click();
    };

    const handleFileChange = async (event) => {
        const selectedFiles = Array.from(event.target.files);

        // TODO: selected model
        const limits = models[0]?.metadata?.limit_mm_per_prompt || {};

        // Note the `type` and `mimetype` fields are not the same.
        const mediaTypes = [
            {
                type: "image",
                current: attachments.filter(a => a.mimetype.startsWith("image/")),
                selected: selectedFiles.filter(a => a.type.startsWith("image/")),
            },
            {
                type: "video",
                current: attachments.filter(a => a.mimetype.startsWith("video/")),
                selected: selectedFiles.filter(a => a.type.startsWith("video/")),
            }
        ];

        for (const { type, current, selected } of mediaTypes) {
            const limit = Number(limits[type]);
            if (limit < current.length + selected.length) {
                const suffix = limit === 1 ? "" : "s";
                setSnackbar({
                    open: true,
                    severity: "error",
                    message: `You can upload up to ${limits[type]} ${type}${suffix} per input.`,
                });
                return;
            }
        }

        // `localUrl` is a temporary URL that can be used before upload finished or re-rendering.
        // Usually I need to use like:
        // `attachment.localUrl || attachment.url`
        const initialAttachments = selectedFiles.map((file) => ({
            name: file.name,
            localUrl: URL.createObjectURL(file),
            mimetype: file.type,
            size: file.size,
            status: "uploading",
            progress: 0,
        }));
        setAttachments((prev) => {
            // Filter existing attachments with the same name.
            const updatedPrev = prev.filter(existingAttachment =>
                !selectedFiles.some(selectedFile => selectedFile.name === existingAttachment.name)
            );
            return [...updatedPrev, ...initialAttachments];
        });

        const onStart = (file, controller) => {
            setUploadRequests((prev) => ({ ...prev, [file.name]: controller }));
        };

        const onProgress = (filename, progress) => {
            setAttachments((prev) =>
                prev.map((attachment) =>
                    attachment.name === filename ? { ...attachment, progress } : attachment
                )
            );
        };

        const onFinish = (filename, url) => {
            setAttachments((prev) =>
                prev.map((attachment) =>
                    attachment.name === filename ? { ...attachment, url: url, status: "uploaded" } : attachment
                )
            );
        };

        for (const file of selectedFiles) {
            try {
                const response = await fetch(`/api/files/upload-url?filename=${file.name}`);
                const url = await response.json();  // The data itself is a URL for now.
                await uploadFile(file, url, "PUT", onStart, onProgress, onFinish);
            } catch (error) {
                // This is a bit hard-coded.
                if (error.message !== "Upload aborted") {
                    console.error("Error during upload:", error);
                    setSnackbar({
                        open: true,
                        severity: "error",
                        message: `Error uploading ${file.name}`,
                    });
                    const failedAttachment = attachments.find((attachment) => attachment.name === file.name);
                    if (failedAttachment) {
                        removeAttachment(failedAttachment);
                    }
                }
            } finally {
                setUploadRequests((prev) => {
                    const newState = { ...prev };
                    delete newState[file.name];
                    return newState;
                });
                // Reset the input field so the same file can be uploaded again.
                // (In case of an error, an abort or user changed the file content etc.)
                if (attachmentsInputRef.current) {
                    attachmentsInputRef.current.value = "";
                }
            }
        }
    };

    const handleRemoveAttachment = (target) => {
        // Abort uploading
        if (uploadRequests[target.name]) {
            uploadRequests[target.name].abort();
        }
        removeAttachment(target);
    };

    const removeAttachment = (target) => {
        // Release Blob URL
        URL.revokeObjectURL(target.localUrl);
        // Remove the attachment from the list.
        setAttachments((prev) => prev.filter((attachment) => attachment.name !== target.name));
    };

    return (
        <div className={styles.inputContainer}>
            <div className={styles.attachments}>
                {attachments.map((attachment, index) => (
                    // I need a wrapper here because:
                    // - I don't want the loading progress to overflow the attachment.
                    // - I however want the removal button to overflow the attachment.
                    <div key={index} className={styles.attachmentWrapper}>
                        <div className={styles.attachment}>
                            {/* These are blob urls, which does not support request params. */}
                            <PreviewImage
                                className={styles.preview}
                                srcSet={attachment.localUrl || attachment.url}
                                src={attachment.localUrl || attachment.url}
                                alt={attachment.name}
                                loading="lazy"
                            />
                            {attachment.status === "uploading" && (
                                <div className={styles.loading}>
                                    <CircularProgress variant="determinate" value={attachment.progress} />
                                </div>
                            )}
                        </div>
                        <button
                            className={styles.removeAttachmentButton}
                            onClick={() => handleRemoveAttachment(attachment)}
                            aria-label={`remove attachment ${attachment.name}`}
                        >
                            <HighlightOffIcon />
                        </button>
                    </div>
                ))}
            </div>
            <form onSubmit={handleSubmit} >
                <label htmlFor="input-text" className={styles.visuallyHidden}>Input chat message</label>
                <textarea
                    id="input-text"
                    className={`${styles.inputText} scroll-box`}
                    ref={inputRef}
                    autoFocus
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <div className={styles.buttonContainer}>
                    <button disabled className={styles.inputButton} onClick={handleUploadButtonClick} aria-label="upload attachments">
                        <AttachFileIcon />
                    </button>
                    <input
                        type="file"
                        accept="image/*,video/*"
                        multiple
                        ref={attachmentsInputRef}
                        onChange={handleFileChange}
                        style={{ display: "none" }}
                    />
                    <button disabled={!ready} className={`${styles.inputButton} ${styles.submitButton}`} type="submit" aria-label="send message">
                        <SendRoundedIcon sx={{ fontSize: "1.5rem" }} />
                    </button>
                </div>
            </form>
        </div>
    );
};

ChatInput.propTypes = {
    onSubmit: PropTypes.func.isRequired,
};

export default ChatInput;
