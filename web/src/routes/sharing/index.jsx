import styles from "./index.module.css";

import { useState, useCallback, useRef } from "react";
import { useLoaderData } from "react-router-dom";

import { useSnackbar } from "@/contexts/snackbar/hook";
import { useInfiniteScroll } from "@/hooks/useInfiniteScroll";

import ShareCard from "./ShareCard";
import EmptyState from "./EmptyState";


// API helper function
const fetchShares = async (size = null, cursor = null) => {
    const apiUrl = new URL("/api/shares", window.location.origin);
    if (cursor) {
        apiUrl.searchParams.set("cursor", cursor);
    }
    if (size) {
        apiUrl.searchParams.set("size", size.toString());
    }

    const response = await fetch(apiUrl.toString());
    if (!response.ok) {
        throw new Error(`Failed to fetch shares: ${response.statusText}`);
    }
    return response.json();
};

async function loader() {
    const data = await fetchShares();
    return {
        shares: data.items || [],
        nextCursor: data.next_page || null,
    };
}

const Sharing = () => {
    const { shares: initialShares, nextCursor: initialCursor } = useLoaderData();

    // State
    const [shares, setShares] = useState(initialShares);
    const [nextCursor, setNextCursor] = useState(initialCursor);
    const [isLoading, setIsLoading] = useState(false);
    const loadMoreRef = useRef();

    // Hooks
    const { setSnackbar } = useSnackbar();

    // Memoized values
    const hasMore = !!nextCursor;

    // Fetch more shares for infinite scrolling
    const fetchMoreShares = useCallback(async () => {
        if (isLoading || !hasMore) {
            return;
        }

        setIsLoading(true);
        try {
            const data = await fetchShares(20, nextCursor);
            setShares(current => [...current, ...(data.items || [])]);
            setNextCursor(data.next_page || null);
        } catch (err) {
            setSnackbar({
                open: true,
                message: `Error loading more shares: ${err.message}`,
                severity: "error",
            });
        } finally {
            setIsLoading(false);
        }
    }, [nextCursor, isLoading, hasMore, setSnackbar]);

    // Set up infinite scroll
    useInfiniteScroll({
        targetRef: loadMoreRef,
        onLoadMore: fetchMoreShares,
        isLoading,
        hasMore,
    });

    // Share actions
    const deleteShare = useCallback(async (shareId) => {
        try {
            const response = await fetch(`/api/shares/${shareId}`, {
                method: "DELETE",
            });
            if (!response.ok) {
                throw new Error(`Failed to delete share: ${response.statusText}`);
            }

            setShares(current => current.filter(share => share.id !== shareId));
            setSnackbar({
                open: true,
                message: "Share deleted successfully",
                severity: "success",
            });
        } catch (err) {
            setSnackbar({
                open: true,
                message: `Error deleting share: ${err.message}`,
                severity: "error",
            });
        }
    }, [setSnackbar]);

    const copyToClipboard = useCallback(async (url) => {
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
    }, [setSnackbar]);

    return (
        <div className={`${styles.sharingContainer} scroll-box`}>
            <div className={styles.sharingContent}>
                <h1 className={styles.sharingTitle}>My Shares</h1>
                <p className={styles.sharingInfo}>
                    Your shared links will remain publicly accessible as long as the related conversation
                    is still saved in your chat history. If any part of the conversation is deleted,
                    its public link will also be removed. When you delete a link, the corresponding
                    conversation in your chat history is not deleted, nor is any content you may have
                    posted on other websites.
                </p>

                {!(shares.length > 0) ? (
                    <EmptyState />
                ) : (
                    <div className={styles.sharesList}>
                        {shares.map((share) => (
                            <ShareCard
                                key={share.id}
                                share={share}
                                onCopy={copyToClipboard}
                                onDelete={deleteShare}
                            />
                        ))}

                        {/* Infinite scroll anchor */}
                        <div ref={loadMoreRef} className={styles.loadMoreAnchor}>
                            {isLoading ? (
                                <div className={styles.spinner} />
                            ) : (
                                <div style={{ width: 24, height: 24, visibility: "hidden" }} />
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Sharing;
Sharing.loader = loader;
