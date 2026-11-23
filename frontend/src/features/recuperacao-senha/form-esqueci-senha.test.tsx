import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { corpoEnviado, renderizar, simularApi, simularApiForaDoAr } from "@/testes/utilitarios";

import { FormEsqueciSenha } from "./form-esqueci-senha";

const MENSAGEM_GENERICA =
  "Se o e-mail estiver cadastrado, você receberá em instantes as instruções para redefinir a senha.";

describe("Tela 'Esqueci minha senha'", () => {
  it("recusa e-mail inválido sem chamar a API", async () => {
    const fetch = simularApi(200, { mensagem: MENSAGEM_GENERICA });
    const { usuario } = renderizar(<FormEsqueciSenha />);

    await usuario.type(screen.getByLabelText("E-mail"), "isto-nao-e-email");
    await usuario.click(screen.getByRole("button", { name: "Enviar instruções" }));

    expect(await screen.findByText("Informe um e-mail válido.")).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("recusa e-mail vazio sem chamar a API", async () => {
    const fetch = simularApi(200, { mensagem: MENSAGEM_GENERICA });
    const { usuario } = renderizar(<FormEsqueciSenha />);

    await usuario.click(screen.getByRole("button", { name: "Enviar instruções" }));

    expect(await screen.findByText("Informe seu e-mail.")).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  // Critério de aceite C1 da issue #6.
  it("envia o e-mail e mostra a mensagem genérica devolvida pela API", async () => {
    const fetch = simularApi(200, { mensagem: MENSAGEM_GENERICA });
    const { usuario } = renderizar(<FormEsqueciSenha />);

    await usuario.type(screen.getByLabelText("E-mail"), "  aluno@example.com ");
    await usuario.click(screen.getByRole("button", { name: "Enviar instruções" }));

    expect(await screen.findByText(MENSAGEM_GENERICA)).toBeInTheDocument();
    expect(fetch.mock.calls[0]?.[0]).toBe("http://localhost:8000/api/v1/auth/esqueci-senha");
    expect(corpoEnviado(fetch)).toEqual({ email: "aluno@example.com" });
    expect(screen.getByRole("link", { name: "Voltar para o login" })).toHaveAttribute(
      "href",
      "/login",
    );
  });

  it("mostra erro amigável quando a API está fora do ar", async () => {
    simularApiForaDoAr();
    const { usuario } = renderizar(<FormEsqueciSenha />);

    await usuario.type(screen.getByLabelText("E-mail"), "aluno@example.com");
    await usuario.click(screen.getByRole("button", { name: "Enviar instruções" }));

    expect(
      await screen.findByText(
        "Não foi possível falar com o servidor. Verifique sua conexão e tente de novo.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Enviar instruções" })).toBeEnabled();
  });
});
