import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { ConversationProvider, conversationReducer, flatConvs, sortConvs, groupConvs, ConversationContext } from './conversation';

// Mock fetch globally
beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve([
        { id: '1', title: 'Conversation 1', created_at: '2024-12-01', last_message_at: '2024-12-25', owner: 'User1', pinned: false },
        { id: '2', title: 'Conversation 2', created_at: '2024-12-02', last_message_at: '2024-12-24', owner: 'User2', pinned: true },
      ]),
    })
  );
});

// Clean up after tests to reset mock
afterEach(() => {
  jest.clearAllMocks();
});

const today = new Date();
const yesterday = new Date().setDate(today.getDate() - 1);


describe('Helper Functions', () => {
  test('flatConvs should flatten grouped conversations', () => {
    const groupedConvs = {
      pinned: [{ id: '2', title: 'Conversation 2' }],
      Today: [{ id: '1', title: 'Conversation 1' }],
    };
    const result = flatConvs(groupedConvs);
    expect(result).toHaveLength(2);
    expect(result[0].title).toBe('Conversation 2');
    expect(result[1].title).toBe('Conversation 1');
  });

  test('sortConvs should sort conversations by pinned and last_message_at', () => {
    const convs = [
      { id: '1', title: 'Conversation 1', last_message_at: '2024-12-25', pinned: false },
      { id: '2', title: 'Conversation 2', last_message_at: '2024-12-24', pinned: true },
    ];
    const sortedConvs = sortConvs(convs);
    expect(sortedConvs[0].title).toBe('Conversation 2');
    expect(sortedConvs[1].title).toBe('Conversation 1');
  });

  test('groupConvs should group conversations by date', () => {
    const convs = [
      { id: '1', title: 'Conversation 1', last_message_at: today },
      { id: '2', title: 'Conversation 2', last_message_at: yesterday },
      { id: '3', title: 'Conversation 3', last_message_at: new Date().setDate(today.getDate() - 2) },
    ];
    const grouped = groupConvs(convs);
    expect(grouped['Today']).toHaveLength(1);
    expect(grouped['Yesterday']).toHaveLength(1);
    expect(grouped['Last seven days']).toHaveLength(1);
  });
});

describe('conversationReducer', () => {
  const initialState = {
    Today: [{ id: '1', title: 'Conversation 1' }],
  };

  test('should handle "added" action', () => {
    const action = {
      type: 'added',
      conv: { id: '2', title: 'Conversation 2' },
    };
    const newState = conversationReducer(initialState, action);
    expect(newState.Today).toHaveLength(2);
  });

  test('should handle "deleted" action', () => {
    const action = { type: 'deleted', convId: '1' };
    const newState = conversationReducer(initialState, action);
    expect(newState.Today).toBeUndefined();
  });

  test.skip('should handle "renamed" action', () => {
    const action = { type: 'renamed', convId: '1', title: 'Updated Title' };
    const newState = conversationReducer(initialState, action);
    expect(newState.Today[0].title).toBe('Updated Title');
  });

  test('should handle "reordered" action', () => {
    const convs = [
      { id: '1', title: 'Conversation 1', last_message_at: today, pinned: false },
      { id: '2', title: 'Conversation 2', last_message_at: yesterday, pinned: true },
    ];
    const action = { type: 'reordered', conv: { id: '1', title: 'Updated Conversation 1' } };
    const newState = conversationReducer({ Today: convs }, action);
    expect(newState.Today[0].title).toBe('Updated Conversation 1');
  });

  test('should handle "replaceAll" action', () => {
    const action = { type: 'replaceAll', groupedConvs: { Today: [], pinned: [] } };
    const newState = conversationReducer(initialState, action);
    expect(newState.Today).toHaveLength(0);
  });
});

describe('ConversationProvider', () => {
  test('fetches and displays conversations', async () => {
    render(
      <ConversationProvider>
        <ConversationContext.Consumer>
          {({ groupedConvs }) => (
            Object.entries(groupedConvs).flatMap(([grp, convs]) => (
              <div>
                {convs.map((conv) => <div key={conv.id}>{conv.title}</div>)}
              </div>
            ))
          )}
        </ConversationContext.Consumer>
      </ConversationProvider>
    );

    // Wait for the async fetch call to resolve
    await act(async () => {
      await new Promise((r) => setTimeout(r, 0));
    });

    expect(screen.getByText('Conversation 1')).toBeInTheDocument();
    expect(screen.getByText('Conversation 2')).toBeInTheDocument();
  });
});
