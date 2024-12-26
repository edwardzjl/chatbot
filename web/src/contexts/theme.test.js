import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";

import { ThemeProvider, ThemeContext } from "./theme";

// Mock localStorage
const mockSetItem = jest.fn();
const mockGetItem = jest.fn();

beforeAll(() => {
    global.Storage.prototype.getItem = mockGetItem;
    global.Storage.prototype.setItem = mockSetItem;
});

afterEach(() => {
    mockSetItem.mockClear();
    mockGetItem.mockClear();
});

describe("ThemeProvider", () => {
    test("renders correctly with default theme", () => {
        mockGetItem.mockReturnValue(null); // Simulate no theme saved in localStorage

        render(
            <ThemeProvider>
                <ThemeContext.Consumer>
                    {({ theme }) => <div>{theme}</div>}
                </ThemeContext.Consumer>
            </ThemeProvider>
        );

        // Check if the default theme is "system"
        expect(screen.getByText("system")).toBeInTheDocument();
    });

    test("renders correctly with theme from localStorage", () => {
        mockGetItem.mockReturnValue("dark"); // Simulate theme being "dark" in localStorage

        render(
            <ThemeProvider>
                <ThemeContext.Consumer>
                    {({ theme }) => <div>{theme}</div>}
                </ThemeContext.Consumer>
            </ThemeProvider>
        );

        // Check if the theme is correctly initialized to "dark"
        expect(screen.getByText("dark")).toBeInTheDocument();
    });

    test("sets the theme and updates localStorage", () => {
        mockGetItem.mockReturnValue("light"); // Simulate theme being "light" in localStorage

        render(
            <ThemeProvider>
                <ThemeContext.Consumer>
                    {({ theme, setTheme }) => (
                        <div>
                            <div>{theme}</div>
                            <button onClick={() => setTheme("dark")}>Set Dark Theme</button>
                        </div>
                    )}
                </ThemeContext.Consumer>
            </ThemeProvider>
        );

        // Check initial theme
        expect(screen.getByText("light")).toBeInTheDocument();

        // Click button to change theme
        fireEvent.click(screen.getByText("Set Dark Theme"));

        // Ensure the theme is updated to "dark"
        expect(screen.getByText("dark")).toBeInTheDocument();

        // Ensure localStorage is updated
        expect(mockSetItem).toHaveBeenCalledWith("theme", "dark");
    });
});
