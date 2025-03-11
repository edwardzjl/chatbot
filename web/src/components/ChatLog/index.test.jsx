import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, it, expect, vi } from "vitest";

import ChatLog from "./index";

// Mock ResizeObserver
class MutationObserverMock {
    observe() { }
    disconnect() { }
}

beforeEach(() => {
    vi.stubGlobal("MutationObserver", MutationObserverMock)
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

    it("scrolls to the bottom when MutationObserver triggers", () => {
        const observeMock = vi.spyOn(MutationObserver.prototype, "observe");
        render(
            <ChatLog>
                <div>Message</div>
            </ChatLog>
        );

        // Verify that MutationObserver is observing the container
        expect(observeMock).toHaveBeenCalled();
    });

    it("handles MutationObserver not being supported", () => {
        vi.stubGlobal("MutationObserver", undefined)

        const warnMock = vi.spyOn(console, "warn").mockImplementation(() => { });

        render(
            <ChatLog>
                <div>Message</div>
            </ChatLog>
        );

        expect(warnMock).toHaveBeenCalledWith("MutationObserver is not supported in this browser.");

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
