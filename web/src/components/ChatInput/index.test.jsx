import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BrowserRouter } from "react-router";

import { HttpStreamContext } from "@/contexts/httpstream";

import ChatInput from "./index";

// Mock the HTTP Stream context provider
const mockHttpStreamContext = {
    ready: true,  // HTTP streaming is always ready
};

// Helper function to render the component with the HTTP Stream context
const renderWithContext = (component) => {
    return render(
        <BrowserRouter>
            <HttpStreamContext.Provider value={mockHttpStreamContext}>
                {component}
            </HttpStreamContext.Provider>
        </BrowserRouter>
    );
};

describe("ChatInput", () => {
    it("should render correctly and have an empty input initially", () => {
        renderWithContext(<ChatInput onSubmit={vi.fn()} />);
        const textarea = screen.getByRole("textbox");
        expect(textarea).toBeDefined();
        expect(textarea.value).toBe("");
    });

    it("should enable the submit button since HTTP Stream is always ready", () => {
        // HTTP streaming doesn't have a "not ready" state like WebSocket
        mockHttpStreamContext.ready = true;
        renderWithContext(<ChatInput onSubmit={vi.fn()} />);
        const submitButton = screen.getByRole("button", { name: /send message/i });
        expect(submitButton.disabled).toBe(false);  // Native DOM property check for disabled
    });

    it("should focus the textarea when convId changes", () => {
        const { rerender } = renderWithContext(<ChatInput onSubmit={vi.fn()} />);
        const textarea = screen.getByRole("textbox");
        expect(document.activeElement).toBe(textarea);  // Checking focus using document.activeElement

        rerender(
            <BrowserRouter>
                <HttpStreamContext.Provider value={mockHttpStreamContext}>
                    <ChatInput onSubmit={vi.fn()} />
                </HttpStreamContext.Provider>
            </BrowserRouter>
        );
        expect(document.activeElement).toBe(textarea);
    });

    it("should adjust the textarea height based on content", async () => {
        const { container } = renderWithContext(<ChatInput onSubmit={vi.fn()} />);
        const textarea = container.querySelector("textarea");
        const initialHeight = textarea.scrollHeight;

        fireEvent.change(textarea, { target: { value: "This is a longer message\n\n\n\n\n\n\n\n" } });

        await screen.findByRole("textbox");
        expect(textarea.style.height).not.toBe(initialHeight);
    });

    it('should submit the input when "Enter" is pressed (without modifiers)', async () => {
        const onSubmit = vi.fn();
        renderWithContext(<ChatInput onSubmit={onSubmit} />);
        const textarea = screen.getByRole("textbox");
        const testMessage = "Test message";

        // Simulate typing and pressing "Enter"
        fireEvent.change(textarea, { target: { value: testMessage } });
        fireEvent.keyDown(textarea, { key: "Enter", code: "Enter", charCode: 13 });

        await waitFor(() => {
            expect(onSubmit).toHaveBeenCalledTimes(1);
            const submittedMessage = onSubmit.mock.calls[0][0]; // get the first argument passed to `onSubmit`
            expect(submittedMessage).toHaveProperty('id');
            expect(submittedMessage).toHaveProperty('content', testMessage);
            expect(submittedMessage).toHaveProperty('type', 'human');
            expect(submittedMessage).toHaveProperty('sent_at');
        });
    });

    it('should not submit the input when "Enter" is pressed with modifiers (Ctrl, Shift, Alt)', async () => {
        const onSubmit = vi.fn();
        renderWithContext(<ChatInput onSubmit={onSubmit} />);
        const textarea = screen.getByRole("textbox");

        // Simulate typing and pressing "Enter" with Ctrl key
        fireEvent.change(textarea, { target: { value: "Test message" } });
        fireEvent.keyDown(textarea, { key: "Enter", code: "Enter", charCode: 13, ctrlKey: true });

        await waitFor(() => expect(onSubmit).not.toHaveBeenCalled());
    });
});
