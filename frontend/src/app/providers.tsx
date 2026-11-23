// PROVISÓRIO: substituir pela implementação da issue [0.3]
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

export function Providers({ children }: { children: ReactNode }) {
  // useState garante um único QueryClient por aba do navegador.
  const [cliente] = useState(
    () => new QueryClient({ defaultOptions: { mutations: { retry: false } } }),
  );
  return <QueryClientProvider client={cliente}>{children}</QueryClientProvider>;
}
