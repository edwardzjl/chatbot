import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import { ThemeContext } from "@/contexts/theme";

import ThemeSelector from "./index";

const setup = () => render(
    <ThemeContext.Provider value={mockThemeContextValue}>
        <ThemeSelector />
    </ThemeContext.Provider>
);

const mockSetTheme = vi.fn();
const mockThemeContextValue = {
    theme: "light",
    setTheme: mockSetTheme,
};


describe("ChatboxHeader", () => {
    it("renders the theme menu and allows theme change", () => {
        setup();
        fireEvent.click(screen.getByText("Theme"));
        expect(screen.getByLabelText("Set theme to light mode")).toBeDefined();
        fireEvent.click(screen.getByLabelText("Set theme to dark mode"));
        expect(mockSetTheme).toHaveBeenCalledWith("dark");
    });
});
