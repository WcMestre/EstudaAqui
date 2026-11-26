import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";
import { vi } from "vitest";

/** Renderiza o componente com o que as telas esperam (TanStack Query). */
export function renderizar(componente: ReactElement) {
  const cliente = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
  return {
    usuario: userEvent.setup(),
    ...render(<QueryClientProvider client={cliente}>{componente}</QueryClientProvider>),
  };
}

/** Faz o fetch responder como a API responderia, sem rede de verdade. */
export function simularApi(status: number, corpo: unknown) {
  return vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify(corpo), {
      status,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

/** Faz o fetch falhar como quando a API está fora do ar. */
export function simularApiForaDoAr() {
  return vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));
}

/** Lê o corpo JSON que foi enviado na chamada número `indice` do fetch. */
export function corpoEnviado(fetch: ReturnType<typeof simularApi>, indice = 0): unknown {
  const opcoes = fetch.mock.calls[indice]?.[1];
  return JSON.parse(String(opcoes?.body));
}
