import { describe, it, expect } from "vitest";

import { parseThinkBlocks } from "./commons";

describe("parseThinkBlocks", () => {
    // Test case 1: Empty string
    it("should return an empty array for an empty string", () => {
        const text = "";
        expect(parseThinkBlocks(text)).toEqual([]);
    });

    // Test case 2: Text with no think blocks
    it("should return a single text segment for text without think blocks", () => {
        const text = "This is just some plain text.";
        expect(parseThinkBlocks(text)).toEqual([
            { type: "text", content: "This is just some plain text." }
        ]);
    });

    // Test case 3: Single think block at the start
    it("should parse a single think block at the start", () => {
        const text = "<think>Thought process.</think>Some text after.";
        expect(parseThinkBlocks(text)).toEqual([
            { type: "think", content: "Thought process." },
            { type: "text", content: "Some text after." }
        ]);
    });

    // Test case 4: Single think block at the end
    it("should parse a single think block at the end", () => {
        const text = "Some text before.<think>Thought process.</think>";
        expect(parseThinkBlocks(text)).toEqual([
            { type: "text", content: "Some text before." },
            { type: "think", content: "Thought process." }
        ]);
    });

    // Test case 5: Single think block in the middle
    it("should parse a single think block in the middle", () => {
        const text = "Before <think>Thought process.</think> After.";
        expect(parseThinkBlocks(text)).toEqual([
            { type: "text", content: "Before " },
            { type: "think", content: "Thought process." },
            { type: "text", content: " After." }
        ]);
    });

    // Test case 6: Multiple think blocks
    it("should parse multiple think blocks correctly", () => {
        const text = "First <think>Thought 1</think> Middle <think>Thought 2</think> Last.";
        expect(parseThinkBlocks(text)).toEqual([
            { type: "text", content: "First " },
            { type: "think", content: "Thought 1" },
            { type: "text", content: " Middle " },
            { type: "think", content: "Thought 2" },
            { type: "text", content: " Last." }
        ]);
    });

    // Test case 7: Empty think block
    it("should parse an empty think block", () => {
        const text = "Text before <think></think> text after.";
        expect(parseThinkBlocks(text)).toEqual([
            { type: "text", content: "Text before " },
            { type: "think", content: "" },
            { type: "text", content: " text after." }
        ]);
    });

    // Test case 8: Think block with content containing newlines but no blank lines
    it("should parse think block content with newlines correctly", () => {
        const text = "<think>Line 1\nLine 2\nLine 3</think>After.";
        expect(parseThinkBlocks(text)).toEqual([
            { type: "think", content: "Line 1\nLine 2\nLine 3" },
            { type: "text", content: "After." }
        ]);
    });

    // Test case 9: Think block with content containing blank lines (Addresses the rehype-raw issue)
    it("should correctly parse think block content with blank lines", () => {
        const text = "<think>First paragraph.\n\nSecond paragraph.</think>Text outside.";
        expect(parseThinkBlocks(text)).toEqual([
            { type: "think", content: "First paragraph.\n\nSecond paragraph." },
            { type: "text", content: "Text outside." }
        ]);
    });

    // Test case 10: Think block with code block inside (multi-line, newlines, backticks)
    it("should correctly parse think block content with code blocks", () => {
        const text = "<think>Some intro.\n\n```javascript\nconst x = 1;\nconsole.log(x);\n```\n\nMore text.</think>End.";
        expect(parseThinkBlocks(text)).toEqual([
            { type: "think", content: "Some intro.\n\n```javascript\nconst x = 1;\nconsole.log(x);\n```\n\nMore text." },
            { type: "text", content: "End." }
        ]);
    });


    // Test case 11: Text starting with what looks like a tag but is incomplete
    it("should treat incomplete or unmatched tags as plain text", () => {
        const text = "<think> This is an unclosed block.";
        // The regex /<think>(.*?)<\/think>/gs won't match, so the whole string is text
        expect(parseThinkBlocks(text)).toEqual([
            { type: "text", content: "<think> This is an unclosed block." }
        ]);
    });

    // Test case 12: Text with an orphaned closing tag
    it("should treat orphaned closing tags as plain text", () => {
        const text = "This is an orphaned </think> tag.";
        // The regex won't match, so the whole string is text
        expect(parseThinkBlocks(text)).toEqual([
            { type: "text", content: "This is an orphaned </think> tag." }
        ]);
    });
});
