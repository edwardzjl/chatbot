import { render, screen, fireEvent } from "@testing-library/react";
import { afterEach, describe, it, expect, vi } from "vitest";

import { ThemeContext } from "./index";
import { ThemeProvider } from "./provider";


const getItemSpy = vi.spyOn(Storage.prototype, "getItem")
const setItemSpy = vi.spyOn(Storage.prototype, "setItem")

afterEach(() => {
    getItemSpy.mockClear() // clear call history
    setItemSpy.mockClear()
    localStorage.clear()
})


describe("ThemeProvider", () => {
    it("renders correctly with default theme", () => {
        getItemSpy.mockReturnValue(null);

        render(
            <ThemeProvider>
                <ThemeContext.Consumer>
                    {({ theme }) => <div>{theme}</div>}
                </ThemeContext.Consumer>
            </ThemeProvider>
        );

        // Check if the default theme is "system"
        expect(screen.getByText("system")).toBeDefined();
    });

    it("renders correctly with theme from localStorage", () => {
        getItemSpy.mockReturnValue("dark");

        render(
            <ThemeProvider>
                <ThemeContext.Consumer>
                    {({ theme }) => <div>{theme}</div>}
                </ThemeContext.Consumer>
            </ThemeProvider>
        );

        // Check if the theme is correctly initialized to "dark"
        expect(screen.getByText("dark")).toBeDefined();
    });

    it("sets the theme and updates localStorage", () => {
        getItemSpy.mockReturnValue("light");

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
        expect(screen.getByText("light")).toBeDefined();

        // Click button to change theme
        fireEvent.click(screen.getByText("Set Dark Theme"));

        // Ensure the theme is updated to "dark"
        expect(screen.getByText("dark")).toBeDefined();

        // Ensure localStorage is updated
        expect(setItemSpy).toHaveBeenCalledWith("theme", "dark")
    });
});
