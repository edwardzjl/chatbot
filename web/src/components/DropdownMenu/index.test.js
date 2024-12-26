import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";

import { Dropdown, DropdownButton, DropdownMenu } from "./index";

describe("DropdownMenu Component", () => {
    test("renders DropdownMenu with children", () => {
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

        expect(screen.getByText("Menu")).toBeInTheDocument();
        expect(screen.getByText("Item 1")).toBeInTheDocument();
        expect(screen.getByText("Item 2")).toBeInTheDocument();
        expect(screen.getByText("Item 3")).toBeInTheDocument();
    });

    test("toggles DropdownList visibility on DropdownHeader click", () => {
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
        expect(screen.queryByRole("menu")).not.toBeInTheDocument();

        // Click to open the dropdown
        fireEvent.click(header);
        expect(screen.getByRole("menu")).toBeVisible();

        // Click to close the dropdown
        fireEvent.click(header);
        expect(screen.queryByRole("menu")).not.toBeInTheDocument();
    });

    test("closes DropdownList when clicking outside", () => {
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
        expect(screen.getByRole("menu")).toBeVisible();

        // Click outside to close
        fireEvent.click(document);
        expect(screen.queryByRole("menu")).not.toBeInTheDocument();
    });

    test("closes DropdownList when an item is clicked", () => {
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
        expect(screen.getByRole("menu")).toBeVisible();

        // Click item to close
        fireEvent.click(item);
        expect(screen.queryByRole("menu")).not.toBeInTheDocument();
    });
});
