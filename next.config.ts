import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
