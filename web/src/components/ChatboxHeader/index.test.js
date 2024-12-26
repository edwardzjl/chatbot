import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";

import { ThemeContext } from "contexts/theme";
import { UserContext } from "contexts/user";

import ChatboxHeader from "./index";

const setup = () => render(
    <ThemeContext.Provider value={mockThemeContextValue}>
    <UserContext.Provider value={mockUserContextValue}>
      <ChatboxHeader />
    </UserContext.Provider>
  </ThemeContext.Provider>
);

const mockSetTheme = jest.fn();
const mockThemeContextValue = {
  theme: "light",
  setTheme: mockSetTheme,
};

const mockUserContextValue = {
  username: "testuser",
  avatar: "testavatar.png",
};

describe("ChatboxHeader", () => {

  test("renders the username and avatar", () => {
    setup();
    expect(screen.getByAltText("testuser's avatar")).toBeInTheDocument();
    expect(screen.getByText("testuser")).toBeInTheDocument();
  });

  test("renders the theme menu and allows theme change", () => {
    setup();
    fireEvent.click(screen.getByText("Theme"));
    expect(screen.getByLabelText("Set theme to light mode")).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText("Set theme to dark mode"));
    expect(mockSetTheme).toHaveBeenCalledWith("dark");
  });

  test("handles logout", () => {
    setup();
    delete window.location;
    window.location = { href: "" };
    fireEvent.click(screen.getByText("Logout"));
    expect(window.location.href).toBe("/oauth2/sign_out");
  });
});
