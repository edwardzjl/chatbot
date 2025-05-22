import { useEffect } from "react";

export function useInfiniteScroll({ targetRef, onLoadMore, hasMore = true, isLoading = false }) {
    useEffect(() => {
        if (!targetRef.current || !hasMore) return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !isLoading) {
                    onLoadMore();
                }
            },
            {
                root: null, // 视口为默认
                rootMargin: "0px",
                threshold: 0.1, // 一小部分可见就触发
            }
        );

        const el = targetRef.current;
        observer.observe(el);

        return () => {
            if (el) observer.unobserve(el);
        };
    }, [targetRef, onLoadMore, isLoading, hasMore]);
}
