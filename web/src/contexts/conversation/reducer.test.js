import { describe, it, expect } from "vitest";
import {
    conversationReducer,
    compareConvs,
    groupConvs,
    getGroupComparisonDates,
    mergeGroupedConvs,
} from "./reducer";

const today = new Date();
const yesterday = new Date().setDate(today.getDate() - 1);

describe('compareConvs', () => {
    it('should prioritize pinned conversations', () => {
        const a = { pinned: true, last_message_at: '2024-01-01T00:00:00Z' };
        const b = { pinned: false, last_message_at: '2025-01-01T00:00:00Z' };
        expect(compareConvs(a, b)).toBe(-1);
        expect(compareConvs(b, a)).toBe(1);
    });

    it('should sort by last_message_at when pinned status is equal (descending)', () => {
        const a = { pinned: false, last_message_at: '2025-01-01T00:00:00Z' };
        const b = { pinned: false, last_message_at: '2024-01-01T00:00:00Z' };
        expect(compareConvs(a, b)).toBe(-1);
        expect(compareConvs(b, a)).toBe(1);
    });

    it('should return 0 for equal pinned status and timestamp', () => {
        const a = { pinned: true, last_message_at: '2025-01-01T00:00:00Z' };
        const b = { pinned: true, last_message_at: '2025-01-01T00:00:00Z' };
        expect(compareConvs(a, b)).toBe(0);
    });

    it('should handle both not pinned and same time as equal', () => {
        const a = { pinned: false, last_message_at: '2023-05-01T12:00:00Z' };
        const b = { pinned: false, last_message_at: '2023-05-01T12:00:00Z' };
        expect(compareConvs(a, b)).toBe(0);
    });

    it('should sort correctly when both pinned but different times', () => {
        const a = { pinned: true, last_message_at: '2025-01-01T00:00:00Z' };
        const b = { pinned: true, last_message_at: '2024-01-01T00:00:00Z' };
        expect(compareConvs(a, b)).toBe(-1);
        expect(compareConvs(b, a)).toBe(1);
    });
});

describe("Test groupConvs", () => {
    it("groupConvs should group conversations by date", () => {
        const convs = [
            { id: "1", title: "Conversation 1", last_message_at: today },
            { id: "2", title: "Conversation 2", last_message_at: yesterday },
            { id: "3", title: "Conversation 3", last_message_at: new Date().setDate(today.getDate() - 2) },
        ];
        const grouped = groupConvs(convs);
        expect(grouped.Today.conversations).toHaveLength(1);
        expect(grouped.Yesterday.conversations).toHaveLength(1);
        expect(grouped["Last Seven Days"].conversations).toHaveLength(1);
    });
});

describe("Test conversationReducer", () => {
    const { today, yesterday } = getGroupComparisonDates();
    const initialState = [{
        key: "Today",
        sortValue: today.getTime(),
        conversations: [{ id: "1", title: "Conversation 1" }],
    }];

    it('should handle "added" action', () => {
        const action = {
            type: "added",
            conv: { id: "2", title: "Conversation 2", last_message_at: today, pinned: false },
        };
        const newState = conversationReducer(initialState, action);
        // length 1 means the conversation was added to the existing (Today)
        expect(newState).toHaveLength(1);
    });

    it('should handle "deleted" action', () => {
        const action = { type: "deleted", conv: { id: "1" } };
        const newState = conversationReducer(initialState, action);
        expect(newState).toHaveLength(0);
    });

    it.skip('should handle "renamed" action', () => {
        const action = { type: "renamed", conv: { id: "1", title: "Updated Title" } };
        const newState = conversationReducer(initialState, action);
        expect(newState[0].conversations[0].title).toBe("Updated Title");
    });

    // TODO: this ut seems wrong
    it('should handle "reordered" action', () => {
        const convs = [
            { id: "1", title: "Conversation 1", last_message_at: today, pinned: false },
            { id: "2", title: "Conversation 2", last_message_at: yesterday, pinned: true },
        ];
        const action = { type: "reordered", conv: { id: "1", title: "Updated Conversation 1" } };
        const newState = conversationReducer([{ key: "Today", conversations: convs }], action);
        expect(newState[0].conversations[0].title).toBe("Conversation 1");
    });

    it('should handle "replaceAll" action', () => {
        const action = { type: "replaceAll", convs: [] };
        const newState = conversationReducer(initialState, action);
        expect(newState).toHaveLength(0);
    });
});

describe('mergeGroupedConvs', () => {
    const makeConv = (id, pinned, lastMessageAt) => ({
        id,
        pinned,
        last_message_at: lastMessageAt,
    });

    it('should merge groups with same key, merging conversations with new overriding old', () => {
        const oldGroups = [
            {
                key: 'group1',
                sortValue: 100,
                conversations: [
                    makeConv('a', false, '2024-01-01T00:00:00Z'),
                    makeConv('b', true, '2024-01-02T00:00:00Z'),
                ],
            },
        ];
        const newGroups = [
            {
                key: 'group1',
                sortValue: 100,
                conversations: [
                    makeConv('b', true, '2024-03-01T00:00:00Z'), // overrides old 'b'
                    makeConv('c', false, '2024-02-01T00:00:00Z'),
                ],
            },
        ];

        const result = mergeGroupedConvs(oldGroups, newGroups);

        expect(result).toHaveLength(1);
        expect(result[0].key).toBe('group1');

        const convIds = result[0].conversations.map(c => c.id);
        expect(convIds).toEqual(['b', 'c', 'a']); // Sorted by pinned + last_message_at
        expect(result[0].conversations.find(c => c.id === 'b').last_message_at).toBe('2024-03-01T00:00:00Z');
    });

    it('should merge with no common keys (just concat in sort order)', () => {
        const oldGroups = [
            { key: 'group1', sortValue: 200, conversations: [makeConv('a', false, '2023-01-01')] },
        ];
        const newGroups = [
            { key: 'group2', sortValue: 100, conversations: [makeConv('b', false, '2023-01-01')] },
        ];

        const result = mergeGroupedConvs(oldGroups, newGroups);

        expect(result.map(g => g.key)).toEqual(['group1', 'group2']); // sorted by sortValue desc
    });

    it('should preserve all groups when one list is empty', () => {
        const oldGroups = [
            { key: 'group1', sortValue: 100, conversations: [makeConv('a', false, '2023-01-01')] },
        ];
        const newGroups = [];

        const result = mergeGroupedConvs(oldGroups, newGroups);
        expect(result).toEqual(oldGroups);
    });

    it('should merge multiple groups in correct order', () => {
        const oldGroups = [
            { key: 'a', sortValue: 300, conversations: [] },
            { key: 'b', sortValue: 200, conversations: [] },
        ];
        const newGroups = [
            { key: 'b', sortValue: 200, conversations: [] },
            { key: 'c', sortValue: 100, conversations: [] },
        ];

        const result = mergeGroupedConvs(oldGroups, newGroups);
        expect(result.map(g => g.key)).toEqual(['a', 'b', 'c']);
    });
});
