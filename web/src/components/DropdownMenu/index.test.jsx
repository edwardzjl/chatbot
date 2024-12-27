import { render, screen, fireEvent } from "@testing-library/react";

import { describe, expect, it } from 'vitest';

import { Dropdown, DropdownButton, DropdownMenu } from "./index";

describe("DropdownMenu Component", () => {
    it("renders DropdownMenu with children", () => {
        render(
            <Dropdown>
                <DropdownButton>Menu</DropdownButton>
                <DropdownMenu>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </DropdownMenu>
            </Dropdown>
        );

        expect(screen.getByText("Menu")).toBeDefined();
        expect(screen.getByText("Item 1")).toBeDefined();
        expect(screen.getByText("Item 2")).toBeDefined();
        expect(screen.getByText("Item 3")).toBeDefined();
    });

    it("toggles DropdownList visibility on DropdownHeader click", () => {
        render(
            <Dropdown>
                <DropdownButton>Menu</DropdownButton>
                <DropdownMenu>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </DropdownMenu>
            </Dropdown>
        );

        const header = screen.getByText("Menu");

        // Initially, the dropdown list should not be visible
        expect(screen.queryByRole("menu")).toBeNull();

        // Click to open the dropdown
        fireEvent.click(header);
        expect(screen.getByRole("menu")).toBeDefined();

        // Click to close the dropdown
        fireEvent.click(header);
        expect(screen.queryByRole("menu")).toBeNull();
    });

    it("closes DropdownList when clicking outside", () => {
        render(
            <Dropdown>
                <DropdownButton>Menu</DropdownButton>
                <DropdownMenu>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </DropdownMenu>
            </Dropdown>
        );

        const header = screen.getByText("Menu");

        // Click to open
        fireEvent.click(header);
        expect(screen.getByRole("menu")).toBeDefined();

        // Click outside to close
        fireEvent.click(document);
        expect(screen.queryByRole("menu")).toBeNull();
    });

    it("closes DropdownList when an item is clicked", () => {
        render(
            <Dropdown>
                <DropdownButton>Menu</DropdownButton>
                <DropdownMenu>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </DropdownMenu>
            </Dropdown>
        );

        const header = screen.getByText("Menu");

        const item = screen.getByText("Item 1");

        // Click to open
        fireEvent.click(header);
        expect(screen.getByRole("menu")).toBeDefined();

        // Click item to close
        fireEvent.click(item);
        expect(screen.queryByRole("menu")).toBeNull();
    });
});
