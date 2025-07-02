import { describe, it, expect } from "vitest";

import { createComparator } from "./commons";

describe("createComparator", () => {
    it("sorts by number ascending", () => {
        const items = [{ age: 30 }, { age: 20 }, { age: 40 }]
        const compare = createComparator([{ key: "age", order: "asc" }])
        const result = items.sort(compare)
        expect(result.map(i => i.age)).toEqual([20, 30, 40])
    })

    it("sorts by number descending", () => {
        const items = [{ age: 30 }, { age: 20 }, { age: 40 }]
        const compare = createComparator([{ key: "age", order: "desc" }])
        const result = items.sort(compare)
        expect(result.map(i => i.age)).toEqual([40, 30, 20])
    })

    it("sorts by string", () => {
        const items = [{ name: "Charlie" }, { name: "Alice" }, { name: "Bob" }]
        const compare = createComparator([{ key: "name", order: "asc" }])
        const result = items.sort(compare)
        expect(result.map(i => i.name)).toEqual(["Alice", "Bob", "Charlie"])
    })

    it("sorts by date descending", () => {
        const items = [
            { updatedAt: new Date("2023-01-01") },
            { updatedAt: new Date("2024-01-01") },
            { updatedAt: new Date("2022-01-01") }
        ]
        const compare = createComparator([{ key: "updatedAt", order: "desc" }])
        const result = items.sort(compare)
        expect(result.map(i => i.updatedAt.getFullYear())).toEqual([2024, 2023, 2022])
    })

    it("handles null values", () => {
        const items = [{ score: null }, { score: 5 }, { score: 10 }]
        const compare = createComparator([{ key: "score", order: "asc" }])
        const result = items.sort(compare)
        expect(result.map(i => i.score)).toEqual([null, 5, 10])
    })

    it("uses custom compareFn when provided", () => {
        const items = [{ a: 1, b: 5 }, { a: 2, b: 2 }]
        const compare = createComparator([
            {
                key: "a",
                compareFn: (x, y) => (x.b - y.b) // compare by b, not a
            }
        ])
        const result = items.sort(compare)
        expect(result.map(i => i.b)).toEqual([2, 5])
    })

    it("supports multi-key fallback sort", () => {
        const items = [
            { pinned: false, updatedAt: new Date("2024-01-01") },
            { pinned: true, updatedAt: new Date("2023-01-01") },
            { pinned: false, updatedAt: new Date("2023-06-01") }
        ]

        const compare = createComparator([
            { key: "pinned", order: "desc" },
            {
                key: "updatedAt",
                order: "desc",
            }
        ])

        const result = items.sort(compare)
        expect(result.map(i => [i.pinned, i.updatedAt.toISOString().slice(0, 10)])).toEqual([
            [true, "2023-01-01"],
            [false, "2024-01-01"],
            [false, "2023-06-01"]
        ])
    })
})
