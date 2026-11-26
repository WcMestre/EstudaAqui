import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async headers() {
    return [
      {
        // A página recebe o token secreto na URL (?token=...). Sem isto, ao
        // clicar num link ou carregar um recurso externo, o navegador poderia
        // enviar a URL completa (com o token) no cabeçalho Referer.
        source: "/redefinir-senha",
        headers: [{ key: "Referrer-Policy", value: "no-referrer" }],
      },
    ];
  },
};

export default nextConfig;
