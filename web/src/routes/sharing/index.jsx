import "./index.css";

import { useState } from "react";
import { Link, useLoaderData } from "react-router-dom";

import { useSnackbar } from "@/contexts/snackbar/hook";
import { formatTimestamp } from "@/commons";

async function loader() {
    const response = await fetch("/api/shares");
    if (!response.ok) {
        throw new Error(`Failed to fetch shares: ${response.statusText}`);
    }
    const shares = await response.json();
    return { shares };
}

const Sharing = () => {
    const { shares: initialShares } = useLoaderData();
    const [shares, setShares] = useState(initialShares);
    const { setSnackbar } = useSnackbar();

    const deleteShare = async (shareId) => {
        try {
            const response = await fetch(`/api/shares/${shareId}`, {
                method: "DELETE",
            });
            if (response.ok) {
                setShares(shares.filter(share => share.id !== shareId));
                setSnackbar({
                    open: true,
                    message: "Share deleted successfully",
                    severity: "success",
                });
            } else {
                throw new Error(`Failed to delete share: ${response.statusText}`);
            }
        } catch (err) {
            setSnackbar({
                open: true,
                message: `Error deleting share: ${err.message}`,
                severity: "error",
            });
        }
    };

    const copyToClipboard = async (url) => {
        try {
            await navigator.clipboard.writeText(url);
            setSnackbar({
                open: true,
                message: "Share URL copied to clipboard",
                severity: "success",
            });
        } catch {
            setSnackbar({
                open: true,
                message: "Failed to copy URL",
                severity: "error",
            });
        }
    };

    return (
        <div className="sharing-container">
            <h1 className="sharing-title">My Shares</h1>
            
            {shares.length === 0 ? (
                <section className="empty-state">
                    <p className="empty-state-text">
                        You haven&apos;t shared any conversations yet.
                    </p>
                    <p className="empty-state-subtext">
                        Share a conversation to see it listed here.
                    </p>
                </section>
            ) : (
                <div>
                    <p className="shares-count">
                        {shares.length} shared conversation{shares.length !== 1 ? 's' : ''}
                    </p>
                    
                    <div className="shares-list">
                        {shares.map((share) => (
                            <div key={share.id} className="share-card">
                                <div className="share-card-content">
                                    <h2 className="share-title">
                                        {share.title}
                                    </h2>
                                    <p className="share-meta">
                                        Created: {formatTimestamp(share.created_at)}
                                    </p>
                                    <p className="share-url">
                                        URL: {share.url}
                                    </p>
                                </div>
                                <div className="share-card-actions">
                                    <Link 
                                        to={`/share/${share.id}`}
                                        className="action-button action-button-primary"
                                        aria-label="View shared conversation"
                                    >
                                        <span className="material-icons">launch</span>
                                        View
                                    </Link>
                                    <button 
                                        className="action-button action-button-secondary"
                                        onClick={() => copyToClipboard(share.url)}
                                        aria-label="Copy share URL"
                                        title="Copy share URL"
                                    >
                                        <span className="material-icons">content_copy</span>
                                    </button>
                                    <button 
                                        className="action-button action-button-danger"
                                        onClick={() => deleteShare(share.id)}
                                        aria-label="Delete share"
                                        title="Delete share"
                                    >
                                        <span className="material-icons">delete</span>
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Sharing;
Sharing.loader = loader;
