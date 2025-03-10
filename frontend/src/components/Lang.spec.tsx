import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Lang from "./Lang";

describe("Lang", () => {
  test("renders", () => {
    render(<Lang />);
    expect(screen.getByText("Français")).toBeDefined();
  });
});
