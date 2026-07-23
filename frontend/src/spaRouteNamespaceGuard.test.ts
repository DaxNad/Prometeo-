import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const appSource = readFileSync(resolve(process.cwd(), "src/App.tsx"), "utf8");
const viteConfigSource = readFileSync(
  resolve(process.cwd(), "vite.config.ts"),
  "utf8"
);

function objectBodyAfter(source: string, marker: string): string {
  const markerIndex = source.indexOf(marker);
  expect(markerIndex).toBeGreaterThanOrEqual(0);

  const openingBraceIndex = source.indexOf("{", markerIndex);
  expect(openingBraceIndex).toBeGreaterThan(markerIndex);

  let depth = 0;
  for (let index = openingBraceIndex; index < source.length; index += 1) {
    if (source[index] === "{") depth += 1;
    if (source[index] !== "}") continue;

    depth -= 1;
    if (depth === 0) {
      return source.slice(openingBraceIndex + 1, index);
    }
  }

  throw new Error(`Object '${marker}' is not closed`);
}

function proxyPrefixes(source: string): string[] {
  const proxyBody = objectBodyAfter(source, "proxy:");

  return Array.from(
    proxyBody.matchAll(/["']([^"']+)["']\s*:/g),
    (match) => match[1]
  )
    .map((key) => {
      if (key === "^/production(/|$)") return "/production";
      return key.startsWith("/") ? key : null;
    })
    .filter((key): key is string => key !== null);
}

function spaRoutes(source: string): string[] {
  return Array.from(
    new Set(
      Array.from(source.matchAll(/["'](\/[^"']*)["']/g), (match) =>
        match[1]
      )
    )
  );
}

function conflictsWithProxyPrefix(
  route: string,
  reservedPrefixes: string[]
): boolean {
  return reservedPrefixes.some((prefix) => route.startsWith(prefix));
}

describe("SPA route namespace guard", () => {
  const reservedPrefixes = proxyPrefixes(viteConfigSource);

  it("keeps every current SPA route outside Vite proxy namespaces", () => {
    expect(reservedPrefixes.length).toBeGreaterThan(0);

    const conflictingRoutes = spaRoutes(appSource).filter((route) =>
      conflictsWithProxyPrefix(route, reservedPrefixes)
    );

    expect(conflictingRoutes).toEqual([]);
  });

  it.each([
    "/app/production-program/image-ocr/acquire",
    "/dashboard",
    "/tl-board",
  ])("accepts SPA route %s", (route) => {
    expect(conflictsWithProxyPrefix(route, reservedPrefixes)).toBe(false);
  });

  it.each([
    "/production-program/image-ocr/acquire",
    "/production/foo",
    "/health/test",
    "/agent-runtime/x",
    "/tl/chat/demo",
  ])("rejects SPA route %s", (route) => {
    expect(conflictsWithProxyPrefix(route, reservedPrefixes)).toBe(true);
  });
});
