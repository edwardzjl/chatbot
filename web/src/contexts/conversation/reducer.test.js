import { describe, it, expect } from "vitest";
import {
    conversationReducer,
    flatConvs,
    sortConvs,
    groupConvs,
} from "./reducer";

const today = new Date();
const yesterday = new Date().setDate(today.getDate() - 1);

describe("Helper Functions", () => {
    it("flatConvs should flatten grouped conversations", () => {
        const groupedConvs = {
            pinned: [{ id: "2", title: "Conversation 2" }],
            Today: [{ id: "1", title: "Conversation 1" }],
        };
        const result = flatConvs(groupedConvs);
        expect(result).toHaveLength(2);
        expect(result[0].title).toBe("Conversation 2");
        expect(result[1].title).toBe("Conversation 1");
    });

    it("sortConvs should sort conversations by pinned and last_message_at", () => {
        const convs = [
            { id: "1", title: "Conversation 1", last_message_at: "2024-12-25", pinned: false },
            { id: "2", title: "Conversation 2", last_message_at: "2024-12-24", pinned: true },
        ];
        const sortedConvs = sortConvs(convs);
        expect(sortedConvs[0].title).toBe("Conversation 2");
        expect(sortedConvs[1].title).toBe("Conversation 1");
    });

    it("groupConvs should group conversations by date", () => {
        const convs = [
            { id: "1", title: "Conversation 1", last_message_at: today },
            { id: "2", title: "Conversation 2", last_message_at: yesterday },
            { id: "3", title: "Conversation 3", last_message_at: new Date().setDate(today.getDate() - 2) },
        ];
        const grouped = groupConvs(convs);
        expect(grouped["Today"]).toHaveLength(1);
        expect(grouped["Yesterday"]).toHaveLength(1);
        expect(grouped["Last seven days"]).toHaveLength(1);
    });
});

describe("conversationReducer", () => {
    const initialState = {
        Today: [{ id: "1", title: "Conversation 1" }],
    };

    it('should handle "added" action', () => {
        const action = {
            type: "added",
            conv: { id: "2", title: "Conversation 2" },
        };
        const newState = conversationReducer(initialState, action);
        expect(newState.Today).toHaveLength(2);
    });

    it('should handle "deleted" action', () => {
        const action = { type: "deleted", convId: "1" };
        const newState = conversationReducer(initialState, action);
        expect(newState.Today).toBeUndefined();
    });

    it.skip('should handle "renamed" action', () => {
        const action = { type: "renamed", convId: "1", title: "Updated Title" };
        const newState = conversationReducer(initialState, action);
        expect(newState.Today[0].title).toBe("Updated Title");
    });

    it('should handle "reordered" action', () => {
        const convs = [
            { id: "1", title: "Conversation 1", last_message_at: today, pinned: false },
            { id: "2", title: "Conversation 2", last_message_at: yesterday, pinned: true },
        ];
        const action = { type: "reordered", conv: { id: "1", title: "Updated Conversation 1" } };
        const newState = conversationReducer({ Today: convs }, action);
        expect(newState.Today[0].title).toBe("Updated Conversation 1");
    });

    it('should handle "replaceAll" action', () => {
        const action = { type: "replaceAll", groupedConvs: { Today: [], pinned: [] } };
        const newState = conversationReducer(initialState, action);
        expect(newState.Today).toHaveLength(0);
    });
});
