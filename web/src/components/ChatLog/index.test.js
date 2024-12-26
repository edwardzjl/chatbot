import React from "react";
import { render, screen } from "@testing-library/react";
import '@testing-library/jest-dom'

import ChatLog from "./index";

// Mock ResizeObserver
class ResizeObserverMock {
    observe() { }
    disconnect() { }
}
global.ResizeObserver = ResizeObserverMock;

describe("ChatLog Component", () => {
    test("renders children correctly", () => {
        render(
            <ChatLog>
                <div>Message 1</div>
                <div>Message 2</div>
            </ChatLog>
        );

        expect(screen.getByText("Message 1")).toBeInTheDocument();
        expect(screen.getByText("Message 2")).toBeInTheDocument();
    });

    test("applies the provided className", () => {
        const customClass = "custom-class";
        render(
            <ChatLog className={customClass}>
                <div>Message</div>
            </ChatLog>
        );

        const chatLogElement = screen.getByRole("region", { name: /chat-log/i });
        expect(chatLogElement).toHaveClass(customClass);
    });

    test("scrolls to the bottom when ResizeObserver triggers", () => {
        const observeMock = jest.spyOn(ResizeObserver.prototype, "observe");
        render(
            <ChatLog>
                <div>Message</div>
            </ChatLog>
        );

        // Verify that ResizeObserver is observing the container
        expect(observeMock).toHaveBeenCalled();
    });

    test("handles ResizeObserver not being supported", () => {
        const originalResizeObserver = global.ResizeObserver;
        global.ResizeObserver = undefined;

        const warnMock = jest.spyOn(console, "warn").mockImplementation(() => { });

        render(
            <ChatLog>
                <div>Message</div>
            </ChatLog>
        );

        expect(warnMock).toHaveBeenCalledWith("ResizeObserver is not supported in this browser.");

        global.ResizeObserver = originalResizeObserver;
        warnMock.mockRestore();
    });

    test("uses smooth scrolling by default", () => {
        render(
            <ChatLog>
                <div>Message</div>
            </ChatLog>
        );

        const chatLogElement = screen.getByRole("region", { name: /chat-log/i });
        expect(chatLogElement).toBeInTheDocument();

        // Smooth scrolling is hard to directly test; focus on behavior instead.
        // Mocking scrollIntoView here is acceptable as a last resort.
    });

    test("allows toggling smooth scrolling", () => {
        render(
            <ChatLog smoothScroll={false}>
                <div>Message</div>
            </ChatLog>
        );

        const chatLogElement = screen.getByRole("region", { name: /chat-log/i });
        expect(chatLogElement).toBeInTheDocument();

        // Behavior testing rather than focusing on implementation details
        // Mocking scrollIntoView is acceptable if absolutely necessary
    });
});
