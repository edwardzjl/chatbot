import styles from "./index.module.css";

import { useState, useEffect } from "react";
import { useLoaderData, useNavigate, useSearchParams } from "react-router-dom";
import Icon from "@mui/material/Icon";

import ChatboxHeader from "@/components/ChatboxHeader";
import { useSnackbar } from "@/contexts/snackbar/hook";
import { formatTimestamp } from "@/commons";
import Pagination from "@/components/Pagination";
import { useDynamicPageSize } from "@/hooks/useDynamicPageSize";

async function loader({ request }) {
    // For initial load, we'll use a minimal loader that just returns empty state
    // The component will fetch data once it calculates the optimal page size
    const url = new URL(request.url);
    const cursor = url.searchParams.get("cursor");
    const size = url.searchParams.get("size");

    // If size is specified (user is navigating), fetch normally
    if (!!!size) {
        // Initial load - return empty state, let component fetch with optimal size
        return {
            shares: [],
            pagination: null,
            requestedSize: null,
            isInitialLoad: true
        };
    }

    const apiUrl = new URL("/api/shares", url.origin);
    if (cursor) {
        apiUrl.searchParams.set("cursor", cursor);
    }
    apiUrl.searchParams.set("size", size);

    const response = await fetch(apiUrl.toString());
    if (!response.ok) {
        throw new Error(`Failed to fetch shares: ${response.statusText}`);
    }
    const data = await response.json();

    return {
        shares: data.items || [],
        pagination: {
            currentPage: data.current_page,
            previousPage: data.previous_page,
            nextPage: data.next_page,
            total: data.total || 0
        },
        requestedSize: parseInt(size, 10),
        isInitialLoad: false
    };
}

const Sharing = () => {
    const { shares: initialShares, pagination: initialPagination, requestedSize, isInitialLoad } = useLoaderData();
    const [shares, setShares] = useState(initialShares);
    const [pagination, setPagination] = useState(initialPagination);
    const [isLoading, setIsLoading] = useState(isInitialLoad);
    const { setSnackbar } = useSnackbar();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    // Dynamic page size calculation
    const { pageSize, containerRef, isCalculated } = useDynamicPageSize({
        minPageSize: 3,
        maxPageSize: 15,
        itemHeight: 120, // Estimated height of each share card
        headerHeight: 150, // Height for header + title + count
        paginationHeight: 80, // Height for pagination component
    });

    // Fetch data with optimal page size
    const fetchSharesWithPageSize = async (size, cursor = null) => {
        setIsLoading(true);
        try {
            const apiUrl = new URL("/api/shares", window.location.origin);
            if (cursor) {
                apiUrl.searchParams.set("cursor", cursor);
            }
            apiUrl.searchParams.set("size", size.toString());

            const response = await fetch(apiUrl.toString());
            if (!response.ok) {
                throw new Error(`Failed to fetch shares: ${response.statusText}`);
            }
            const data = await response.json();

            setShares(data.items || []);

            // Since API always returns total as null for cursor-based pagination,
            // we'll set total to null and let the pagination component handle it
            setPagination({
                currentPage: data.current_page,
                previousPage: data.previous_page,
                nextPage: data.next_page,
                total: null // Always null for cursor-based pagination
            });
        } catch (err) {
            setSnackbar({
                open: true,
                message: `Error fetching shares: ${err.message}`,
                severity: "error",
            });
        } finally {
            setIsLoading(false);
        }
    };

    // Fetch data when optimal page size is calculated (initial load)
    useEffect(() => {
        if (isCalculated && isInitialLoad) {
            console.log(`Fetching initial data with optimal page size: ${pageSize}`);
            fetchSharesWithPageSize(pageSize);
        }
    }, [isCalculated, pageSize, isInitialLoad]);

    // Handle page size changes for subsequent loads
    useEffect(() => {
        if (isCalculated && !isInitialLoad && requestedSize && pageSize !== requestedSize) {
            console.log(`Reloading with optimal page size: ${pageSize} (was ${requestedSize})`);
            const newSearchParams = new URLSearchParams(searchParams);
            newSearchParams.set("size", pageSize.toString());
            // Reset cursor to start from beginning with new page size
            newSearchParams.delete("cursor");
            navigate(`?${newSearchParams.toString()}`, { replace: true });
        }
    }, [isCalculated, pageSize, requestedSize, searchParams, navigate, isInitialLoad]);

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

    const goToPage = (cursor) => {
        const params = new URLSearchParams(searchParams);
        if (cursor) {
            params.set("cursor", cursor);
        } else {
            params.delete("cursor");
        }
        // Ensure we use the calculated page size for navigation
        params.set("size", pageSize.toString());
        navigate(`/sharing?${params.toString()}`);
    };

    const nextPage = () => {
        if (pagination && pagination.nextPage) {
            goToPage(pagination.nextPage);
        }
    };

    const prevPage = () => {
        if (pagination && pagination.previousPage) {
            goToPage(pagination.previousPage);
        }
    };

    return (
        <div className={styles.sharingContainer}>
            <ChatboxHeader />
            <div className={styles.sharingContent} ref={containerRef}>
                <h1 className={styles.sharingTitle}>My Shares</h1>

                {isLoading ? (
                    <section className={styles.emptyState}>
                        <p className={styles.EmptyStateText}>
                            Loading shares...
                        </p>
                        <p className={styles.emptyStateSubtext}>
                            Optimizing layout for your screen size
                        </p>
                    </section>
                ) : shares.length === 0 ? (
                    <section className={styles.emptyState}>
                        <p className={styles.EmptyStateText}>
                            You haven&apos;t shared any conversations yet.
                        </p>
                        <p className={styles.emptyStateSubtext}>
                            Share a conversation to see it listed here.
                        </p>
                    </section>
                ) : (
                    <div>
                        <p className={styles.sharesCount}>
                            {shares.length} shared conversation{shares.length !== 1 ? 's' : ''}
                            {isCalculated && (
                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                                    • Showing {pageSize} per page (optimized for your screen)
                                </span>
                            )}
                        </p>

                        <div className={styles.sharesList}>
                            {shares.map((share) => (
                                <div key={share.id} className={styles.shareCard}>
                                    <div className={styles.shareCardContent}>
                                        <h2 className={styles.shareTitle}>
                                            {share.title}
                                        </h2>
                                        <p className={styles.shareMeta}>
                                            Created: {formatTimestamp(share.created_at)}
                                        </p>
                                        <a
                                            href={share.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className={styles.shareUrl}
                                        >
                                            {share.url}
                                        </a>
                                    </div>
                                    <div className={styles.shareCardActions}>
                                        <button
                                            className={styles.actionButton}
                                            onClick={() => copyToClipboard(share.url)}
                                            aria-label="Copy share URL"
                                            title="Copy share URL"
                                        >
                                            <Icon baseClassName="material-symbols-outlined">content_copy</Icon>
                                        </button>
                                        <button
                                            className={`${styles.actionButton} ${styles.actionButtonDanger}`}
                                            onClick={() => deleteShare(share.id)}
                                            aria-label="Delete share"
                                            title="Delete share"
                                        >
                                            <Icon baseClassName="material-symbols-outlined">delete</Icon>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {pagination && (
                            <Pagination
                                currentPage={pagination.currentPage}
                                previousPage={pagination.previousPage}
                                nextPage={pagination.nextPage}
                                total={pagination.total}
                                onPrevious={prevPage}
                                onNext={nextPage}
                            />
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Sharing;
Sharing.loader = loader;
