import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderizar } from "@/testes/utilitarios";

import { FormLogin } from "./form-login";

describe("Tela de login", () => {
  // Critério de aceite C1 da issue #6.
  it("mostra o link 'Esqueci minha senha' apontando para /esqueci-senha", () => {
    renderizar(<FormLogin />);

    const link = screen.getByRole("link", { name: "Esqueci minha senha" });

    expect(link).toHaveAttribute("href", "/esqueci-senha");
  });
});
