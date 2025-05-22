import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

import { ConversationContext } from "./index";
import { ConversationProvider } from "./provider";

// Mock the global fetch function
vi.stubGlobal('fetch', vi.fn());

// Mock fetch globally
beforeEach(() => {
    const mockResponse = {
        items: [
            {
                id: '1',
                title: 'Conversation 1',
                created_at: '2024-12-01',
                last_message_at: '2024-12-25',
                owner: 'User1',
                pinned: false,
            },
            {
                id: '2',
                title: 'Conversation 2',
                created_at: '2024-12-02',
                last_message_at: '2024-12-24',
                owner: 'User2',
                pinned: true,
            },
        ]
    };
    fetch.mockResolvedValueOnce({
        json: vi.fn().mockResolvedValueOnce(mockResponse),
    });
});

// Clean up after tests to reset mock
afterEach(() => {
    vi.clearAllMocks();
});


describe('ConversationProvider', () => {
    it('fetches and displays conversations', async () => {
        render(
            <ConversationProvider>
                <ConversationContext.Consumer>
                    {({ groupedConvsArray }) =>
                        groupedConvsArray.map(group => (
                            <div key={group.key}>
                                {group.conversations.map((conv) => (
                                    <div key={conv.id}>{conv.title}</div>
                                ))}
                            </div>
                        ))
                    }
                </ConversationContext.Consumer>
            </ConversationProvider>
        );

        // Wait for the async fetch call to resolve
        await act(async () => {
            await new Promise((r) => setTimeout(r, 0));
        });

        expect(screen.getByText('Conversation 1')).toBeDefined();
        expect(screen.getByText('Conversation 2')).toBeDefined();
    });
});
