import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { corpoEnviado, renderizar, simularApi } from "@/testes/utilitarios";

import { FormRedefinirSenha } from "./form-redefinir-senha";

function abrirLink(token = "token-do-email") {
  window.history.replaceState(null, "", `/redefinir-senha?token=${token}`);
}

async function preencher(
  usuario: ReturnType<typeof renderizar>["usuario"],
  senha: string,
  confirmacao = senha,
) {
  await usuario.type(screen.getByLabelText("Nova senha"), senha);
  await usuario.type(screen.getByLabelText("Confirme a nova senha"), confirmacao);
  await usuario.click(screen.getByRole("button", { name: "Salvar nova senha" }));
}

function esperarOfertaDeNovoLink() {
  expect(screen.getByRole("link", { name: "Pedir novo link" })).toHaveAttribute(
    "href",
    "/esqueci-senha",
  );
  expect(screen.queryByLabelText("Nova senha")).not.toBeInTheDocument();
}

describe("Tela 'Redefinir senha'", () => {
  it("tira o token da URL assim que a página carrega e o usa no envio", async () => {
    abrirLink("abc123");
    const fetch = simularApi(200, { mensagem: "Senha redefinida com sucesso." });
    const { usuario } = renderizar(<FormRedefinirSenha />);

    await screen.findByLabelText("Nova senha");
    expect(window.location.search).toBe("");
    expect(window.location.pathname).toBe("/redefinir-senha");

    await preencher(usuario, "SenhaNova456");

    expect(corpoEnviado(fetch)).toEqual({ token: "abc123", nova_senha: "SenhaNova456" });
  });

  it("exige pelo menos 8 caracteres sem chamar a API", async () => {
    abrirLink();
    const fetch = simularApi(200, {});
    const { usuario } = renderizar(<FormRedefinirSenha />);

    await preencher(usuario, "1234567");

    expect(
      await screen.findByText("A nova senha deve ter pelo menos 8 caracteres."),
    ).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("exige que a confirmação seja igual à nova senha", async () => {
    abrirLink();
    const fetch = simularApi(200, {});
    const { usuario } = renderizar(<FormRedefinirSenha />);

    await preencher(usuario, "SenhaNova456", "SenhaNova457");

    expect(await screen.findByText("As senhas não conferem.")).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  // Critério de aceite C3 da issue #6.
  it("mostra a confirmação e o caminho para entrar com a nova senha", async () => {
    abrirLink();
    simularApi(200, { mensagem: "Senha redefinida com sucesso. Entre com a nova senha." });
    const { usuario } = renderizar(<FormRedefinirSenha />);

    await preencher(usuario, "SenhaNova456");

    expect(
      await screen.findByText("Senha redefinida com sucesso. Entre com a nova senha."),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Entrar" })).toHaveAttribute("href", "/login");
  });

  // Critério de aceite C4 da issue #6 (os três casos de link recusado).
  it.each([
    ["link_expirado", "Este link expirou (ele vale por 1 hora). Peça um novo link."],
    ["link_ja_usado", "Este link já foi usado. Se precisar, peça um novo link."],
    ["link_invalido", "Este link de redefinição não é válido. Peça um novo link."],
  ])("%s: mostra a mensagem clara e oferece pedir outro link", async (codigo, mensagem) => {
    abrirLink();
    simularApi(400, { codigo, mensagem });
    const { usuario } = renderizar(<FormRedefinirSenha />);

    await preencher(usuario, "SenhaNova456");

    expect(await screen.findByText(mensagem)).toBeInTheDocument();
    esperarOfertaDeNovoLink();
  });

  it("sem token na URL: avisa e oferece pedir outro link", async () => {
    window.history.replaceState(null, "", "/redefinir-senha");
    renderizar(<FormRedefinirSenha />);

    expect(
      await screen.findByText("Este link de redefinição não é válido. Peça um novo link."),
    ).toBeInTheDocument();
    esperarOfertaDeNovoLink();
  });

  it("erro que não é do link mantém o formulário para tentar de novo", async () => {
    abrirLink();
    simularApi(422, {
      codigo: "dados_invalidos",
      mensagem: "A nova senha deve ter no máximo 128 caracteres.",
    });
    const { usuario } = renderizar(<FormRedefinirSenha />);

    await preencher(usuario, "SenhaNova456");

    expect(
      await screen.findByText("A nova senha deve ter no máximo 128 caracteres."),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Nova senha")).toBeInTheDocument();
  });
});
