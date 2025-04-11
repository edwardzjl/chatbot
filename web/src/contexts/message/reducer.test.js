import { describe, it, expect } from "vitest";
import { deepMerge } from "./reducer";

describe("deepMerge", () => {
    it("should handle null and undefined values correctly", () => {
        const a = { foo: "a", bar: "b" };
        const b = { foo: undefined, bar: null, baz: "c" };

        const result = deepMerge(a, b);
        expect(result).toEqual({
            foo: "a",
            bar: "b",
            baz: "c"
        });
    });

    it("should concat strings", () => {
        const a = { foo: "a", bar: "b" };
        const b = { foo: "b", foobar: "c" };

        const result = deepMerge(a, b);
        expect(result).toEqual({
            foo: "ab",
            bar: "b",
            foobar: "c"
        });
    });

    it("should add numbers together", () => {
        const a = { count: 1 };
        const b = { count: 2 };

        const result = deepMerge(a, b);
        expect(result).toEqual({
            count: 3 // Numbers should be added
        });
    });

    it("should concatenate arrays", () => {
        const a = { list: [1, 2] };
        const b = { list: [3, 4] };

        const result = deepMerge(a, b);
        expect(result).toEqual({
            list: [1, 2, 3, 4]
        });
    });

    it("should replace non-matching types", () => {
        const a = { foo: "a", bar: 1 };
        const b = { foo: 2, bar: "b" };

        const result = deepMerge(a, b);
        expect(result).toEqual({
            foo: 2,
            bar: "b"
        });
    });

    it("should recursively merge nested objects", () => {
        const a = { nested: { deep: { key: "a" } } };
        const b = { nested: { deep: { key: "b", newKey: "c" } } };

        const result = deepMerge(a, b);
        expect(result).toEqual({
            nested: { deep: { key: "ab", newKey: "c" } }
        });
    });

    it("should not modify the original objects", () => {
        const a = { foo: "a" };
        const b = { foo: "b" };

        deepMerge(a, b);
        expect(a).toEqual({ foo: "a" }); // Ensure a is not mutated
        expect(b).toEqual({ foo: "b" }); // Ensure b is not mutated
    });

});
