import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import { ThemeContext } from "@/contexts/theme";
import { UserContext } from "@/contexts/user";

import ChatboxHeader from "./index";

const setup = () => render(
    <ThemeContext.Provider value={mockThemeContextValue}>
        <UserContext.Provider value={mockUserContextValue}>
            <ChatboxHeader />
        </UserContext.Provider>
    </ThemeContext.Provider>
);

const mockSetTheme = vi.fn();
const mockThemeContextValue = {
    theme: "light",
    setTheme: mockSetTheme,
};

const mockUserContextValue = {
    username: "testuser",
    avatar: "testavatar.png",
};

describe("ChatboxHeader", () => {
    it("renders the username and avatar", () => {
        setup();
        expect(screen.getByAltText("testuser's avatar")).toBeDefined();
        expect(screen.getByText("testuser")).toBeDefined();
    });

    it("renders the theme menu and allows theme change", () => {
        setup();
        fireEvent.click(screen.getByText("Theme"));
        expect(screen.getByLabelText("Set theme to light mode")).toBeDefined();
        fireEvent.click(screen.getByLabelText("Set theme to dark mode"));
        expect(mockSetTheme).toHaveBeenCalledWith("dark");
    });

    it("handles logout", () => {
        setup();
        delete window.location;
        window.location = { href: "" };
        fireEvent.click(screen.getByText("Logout"));
        expect(window.location.href).toBe("/oauth2/sign_out");
    });
});
