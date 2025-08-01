import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

import ThemeSelector from "./index";

// Mock the useTheme hook
vi.mock("@/hooks/useTheme", () => ({
    useTheme: vi.fn(),
}));

import { useTheme } from "@/hooks/useTheme";

const mockSetTheme = vi.fn();

const setup = (themeValue = "light") => {
    useTheme.mockReturnValue({
        theme: themeValue,
        codeTheme: {},
        setTheme: mockSetTheme,
    });

    return render(<ThemeSelector />);
};

describe("ThemeSelector", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it("renders the theme menu and allows theme change", () => {
        setup();
        fireEvent.click(screen.getByText("Theme"));
        expect(screen.getByLabelText("Set theme to light mode")).toBeDefined();
        fireEvent.click(screen.getByLabelText("Set theme to dark mode"));
        expect(mockSetTheme).toHaveBeenCalledWith("dark");
    });

    it("shows correct selected theme", () => {
        setup("dark");
        fireEvent.click(screen.getByText("Theme"));
        const darkButton = screen.getByLabelText("Set theme to dark mode");
        expect(darkButton.className).toContain("selected");
    });
});
