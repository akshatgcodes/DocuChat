import { describe, expect, it } from "vitest";
import { formatBytes, segments } from "./answer";

describe("segments", () => {
  const known = new Set([1, 2, 3]);

  it("turns citation markers into cite segments", () => {
    expect(segments("Adam was used [1]. Rate warmed up [2][3].", known)).toEqual([
      { kind: "text", text: "Adam was used " },
      { kind: "cite", n: 1 },
      { kind: "text", text: ". Rate warmed up " },
      { kind: "cite", n: 2 },
      { kind: "cite", n: 3 },
      { kind: "text", text: "." },
    ]);
  });

  it("handles comma lists", () => {
    expect(segments("Both [1, 3]", known).filter((s) => s.kind === "cite")).toEqual([
      { kind: "cite", n: 1 },
      { kind: "cite", n: 3 },
    ]);
  });

  it("leaves unknown numbers and other brackets as text", () => {
    expect(segments("See [7] and [a] and arr[0]", known)).toEqual([{ kind: "text", text: "See [7] and [a] and arr[0]" }]);
  });
});

describe("formatBytes", () => {
  it("picks a unit", () => {
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(2_215_244)).toBe("2.1 MB");
  });
});
