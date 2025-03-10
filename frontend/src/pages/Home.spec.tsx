import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import Home from "./Home";

describe("Home", () => {
  test("renders", () => {
    render(<Home />);
    expect(screen.getByText("Under construction")).toBeDefined();
  });
});
