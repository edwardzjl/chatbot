import { render, screen, fireEvent } from "@testing-library/react";
import { beforeEach, describe, it, expect, vi } from "vitest";
import PropTypes from 'prop-types';

import { WebsocketContext } from "@/contexts/websocket";
import ChatInput from "./index";

// Mock WebsocketContext provider
const MockWebsocketContextProvider = ({ children }) => {
    const mockContextValue = {ready: true};  // Mock the 'ready' value as 'true'
    return (
        <WebsocketContext.Provider value={mockContextValue}>
            {children}
        </WebsocketContext.Provider>
    );
};
MockWebsocketContextProvider.propTypes = {
    children: PropTypes.node.isRequired,
};

describe("ChatInput component", () => {
    let mockOnSubmit;

    beforeEach(() => {
    // Mock the onSubmit function before each test
        mockOnSubmit = vi.fn();
    });

    it("renders the textarea and submit button", () => {
        render(
            <MockWebsocketContextProvider>
                <ChatInput onSubmit={mockOnSubmit} />
            </MockWebsocketContextProvider>
        );

        // Check if the textarea and submit button are rendered
        expect(screen.getByRole('textbox')).toBeDefined();
        expect(screen.getByRole('button')).toBeDefined();
    });

    it("calls onSubmit with input value when form is submitted", () => {
        render(
            <MockWebsocketContextProvider>
                <ChatInput onSubmit={mockOnSubmit} />
            </MockWebsocketContextProvider>
        );

        const input = screen.getByRole('textbox');
        const submitButton = screen.getByRole('button');

        // Simulate typing in the textarea
        fireEvent.change(input, { target: { value: 'Hello, world!' } });

        // Simulate clicking the submit button
        fireEvent.click(submitButton);

        // Verify that the onSubmit function was called with the correct input
        expect(mockOnSubmit).toHaveBeenCalledWith('Hello, world!');
    });

    it("clears the input field after submission", () => {
        render(
            <MockWebsocketContextProvider>
                <ChatInput onSubmit={mockOnSubmit} />
            </MockWebsocketContextProvider>
        );

        const input = screen.getByRole('textbox');
        const submitButton = screen.getByRole('button');

        // Simulate typing in the textarea
        fireEvent.change(input, { target: { value: 'Hello, world!' } });

        // Submit the form
        fireEvent.click(submitButton);

        // Verify that the input field is cleared
        expect(input.value).toBe('');
    });

    it("handles Enter key press to submit the form", () => {
        render(
            <MockWebsocketContextProvider>
                <ChatInput onSubmit={mockOnSubmit} />
            </MockWebsocketContextProvider>
        );

        const input = screen.getByRole('textbox');

        // Simulate typing in the textarea
        fireEvent.change(input, { target: { value: 'Hello, world!' } });

        // Simulate pressing Enter key without any modifier
        fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

        // Verify that the onSubmit function was called
        expect(mockOnSubmit).toHaveBeenCalledWith('Hello, world!');
    });

    it("does not submit the form when Enter is pressed with modifier keys", () => {
        render(
            <MockWebsocketContextProvider>
                <ChatInput onSubmit={mockOnSubmit} />
            </MockWebsocketContextProvider>
        );

        const input = screen.getByRole('textbox');

        // Simulate typing in the textarea
        fireEvent.change(input, { target: { value: 'Hello, world!' } });

        // Simulate pressing Enter with Ctrl key
        fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', ctrlKey: true });

        // Verify that the onSubmit function was NOT called
        expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it("adjusts the height of the textarea based on content", async () => {
        render(
            <MockWebsocketContextProvider>
                <ChatInput onSubmit={mockOnSubmit} />
            </MockWebsocketContextProvider>
        );

        const input = screen.getByRole('textbox');

        // Initial height
        const initialHeight = input.height;

        // Simulate typing to change the content
        fireEvent.change(input, { target: { value: 'This is a longer message\n\n\n\n\n\n\n\n' } });

        await screen.findByRole('textbox');

        // Check if the height changed (after typing)
        expect(input.style.height).not.toBe(initialHeight);
    });
});
