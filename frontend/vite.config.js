import { defineConfig } from "vite";
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons';
import path from 'path';
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    createSvgIconsPlugin({
      iconDirs: [path.resolve(process.cwd(), 'src/assets/icons')],
      symbolId: 'icon-[name]',
    }),
  ],
  assetsInclude: ["**/*.md"],
  publicDir: "public",
  css: {
    preprocessorOptions: {
      scss: {
        silenceDeprecations: ["legacy-js-api", "import", "global-builtin", "color-functions", "if-function"],
      },
    },
  },
  server: {
    proxy: {
      "/p/": {
        target: "https://nyrkio.com/",
        changeOrigin: true,
      },
      "/api": {
        //target: process.env.VITE_API_TARGET || "http://localhost:8000",
        target: "https://staging.nyrkio.com",
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: "localhost",
        configure: (proxy) => {
          proxy.on("proxyReq", (proxyReq) => {
            proxyReq.setHeader("origin", "https://staging.nyrkio.com");
            proxyReq.setHeader("referer", "https://staging.nyrkio.com/");
          });
          proxy.on("proxyRes", (proxyRes) => {
            const setCookie = proxyRes.headers["set-cookie"];
            if (setCookie) {
              proxyRes.headers["set-cookie"] = setCookie.map((c) =>
                c.replace(/;\s*Secure/i, ""),
              );
            }
          });
        },
      },
    },
  },
});