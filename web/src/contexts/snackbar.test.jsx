import React, { useContext } from "react";
import { render, screen, fireEvent } from "@testing-library/react";

import { SnackbarProvider, SnackbarContext } from "./snackbar";

// Test component to consume the context
const TestComponent = () => {
    const { snackbar, setSnackbar } = useContext(SnackbarContext);

    const handleClick = () => {
        setSnackbar({ open: true, severity: "error", message: "Test error message" });
    };

    return (
        <div>
            <button onClick={handleClick}>Show Snackbar</button>
            <div>{snackbar.message || "No message"}</div>  {/* Add a default message to make tests easier.*/}
            <div>{snackbar.severity}</div>
            <div>{snackbar.open ? "Snackbar is open" : "Snackbar is closed"}</div>
        </div>
    );
};

describe("SnackbarProvider", () => {
    it("should render children components correctly", () => {
        render(
            <SnackbarProvider>
                <div>Test Child</div>
            </SnackbarProvider>
        );
        expect(screen.getByText("Test Child")).toBeInTheDocument();
    });

    it("should provide the correct default values for snackbar", () => {
        render(
            <SnackbarProvider>
                <TestComponent />
            </SnackbarProvider>
        );

        // Check the default values of snackbar
        expect(screen.getByText("No message")).toBeInTheDocument();  // Default message
        expect(screen.getByText("info")).toBeInTheDocument();  // Default severity
        expect(screen.getByText("Snackbar is closed")).toBeInTheDocument();  // Default open state
    });

    it("should update the snackbar context when setSnackbar is called", () => {
        render(
            <SnackbarProvider>
                <TestComponent />
            </SnackbarProvider>
        );

        const button = screen.getByText("Show Snackbar");
        fireEvent.click(button);

        // Check if snackbar values are updated
        expect(screen.getByText("Test error message")).toBeInTheDocument();
        expect(screen.getByText("error")).toBeInTheDocument();
        expect(screen.getByText("Snackbar is open")).toBeInTheDocument();
    });
});
