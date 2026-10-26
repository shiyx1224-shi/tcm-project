import type { NextConfig } from "next";

const isGitHubPages = process.env.GITHUB_PAGES === "1";

const nextConfig: NextConfig = {
  images: { unoptimized: true },
  /* Static export for the public GitHub Pages teaching UI. */
  ...(isGitHubPages
    ? {
        output: "export" as const,
        basePath: "/tcm-project",
        assetPrefix: "/tcm-project",
        trailingSlash: true,
      }
    : {}),
  /* Keep client interactivity reliable in this teaching app.
     cacheComponents/partialPrefetching were leaving a static shell
     without usable client event handlers in local testing. */
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
