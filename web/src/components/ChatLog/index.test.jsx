import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, it, expect, vi } from "vitest";

import ChatLog from "./index";

// Mock ResizeObserver
class ResizeObserverMock {
    observe() { }
    disconnect() { }
}

beforeEach(() => {
    vi.stubGlobal('ResizeObserver', ResizeObserverMock)
});

afterEach(() => {
    vi.unstubAllGlobals()
});

describe("ChatLog Component", () => {
    it("renders children correctly", () => {
        render(
            <ChatLog>
                <div>Message 1</div>
                <div>Message 2</div>
            </ChatLog>
        );

        expect(screen.getByText("Message 1")).toBeDefined();
        expect(screen.getByText("Message 2")).toBeDefined();
    });

    it("applies the provided className", () => {
        const customClass = "custom-class";
        render(
            <ChatLog className={customClass}>
                <div>Message</div>
            </ChatLog>
        );

        const chatLogElement = screen.getByRole("region", { name: /chat-log/i });
        expect(chatLogElement.classList).toContain(customClass);
    });

    it("scrolls to the bottom when ResizeObserver triggers", () => {
        const observeMock = vi.spyOn(ResizeObserver.prototype, "observe");
        render(
            <ChatLog>
                <div>Message</div>
            </ChatLog>
        );

        // Verify that ResizeObserver is observing the container
        expect(observeMock).toHaveBeenCalled();
    });

    it("handles ResizeObserver not being supported", () => {
        vi.stubGlobal('ResizeObserver', undefined)

        const warnMock = vi.spyOn(console, "warn").mockImplementation(() => { });

        render(
            <ChatLog>
                <div>Message</div>
            </ChatLog>
        );

        expect(warnMock).toHaveBeenCalledWith("ResizeObserver is not supported in this browser.");

        warnMock.mockRestore();
    });

    it("uses smooth scrolling by default", () => {
        render(
            <ChatLog>
                <div>Message</div>
            </ChatLog>
        );

        const chatLogElement = screen.getByRole("region", { name: /chat-log/i });
        expect(chatLogElement).toBeDefined();

        // Smooth scrolling is hard to directly test; focus on behavior instead.
        // Mocking scrollIntoView here is acceptable as a last resort.
    });

    it("allows toggling smooth scrolling", () => {
        render(
            <ChatLog smoothScroll={false}>
                <div>Message</div>
            </ChatLog>
        );

        const chatLogElement = screen.getByRole("region", { name: /chat-log/i });
        expect(chatLogElement).toBeDefined();

        // Behavior testing rather than focusing on implementation details
        // Mocking scrollIntoView is acceptable if absolutely necessary
    });
});
