import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Navbar from "./Navbar";

describe("Navbar", () => {
  test("renders", () => {
    render(<Navbar />);
    expect(screen.getByText("Taram")).toBeDefined();
  });
});
