import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import NotFound from "./NotFound";

describe("NotFound", () => {
  test("renders", () => {
    render(<NotFound />);
    expect(screen.getByText("Page not found")).toBeDefined();
  });
});
