/**
 * Teste ponta a ponta da recuperação de senha (issue #6).
 *
 * Diferente dos testes de unidade, aqui nada é simulado: o navegador abre as
 * telas, a API grava no Postgres e o e-mail passa de verdade pelo Mailpit.
 */
import { expect, test, type Page } from "@playwright/test";

import { URL_API, URL_FRONT } from "./enderecos";
import { esvaziarCaixa, lerLinkDeRedefinicao } from "./mailpit";
import { USUARIOS } from "./usuarios";

const NOVA_SENHA = "SenhaNova456";

async function entrar(page: Page, email: string, senha: string) {
  await page.goto("/login");
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Senha", { exact: true }).fill(senha);
  await page.getByRole("button", { name: "Entrar" }).click();
}

async function salvarNovaSenha(page: Page, senha: string) {
  await page.getByLabel("Nova senha", { exact: true }).fill(senha);
  await page.getByLabel("Confirme a nova senha").fill(senha);
  await page.getByRole("button", { name: "Salvar nova senha" }).click();
}

test("pedir o link, ler o e-mail, redefinir a senha e entrar com a nova senha", async ({
  page,
}) => {
  const { email, nome, senha: senhaAntiga } = USUARIOS.fluxoCompleto;
  await esvaziarCaixa(email);

  // C1: "Esqueci minha senha" na tela de login, com a mensagem genérica.
  await page.goto("/login");
  await page.getByRole("link", { name: "Esqueci minha senha" }).click();
  await expect(page).toHaveURL(/\/esqueci-senha$/);
  await page.getByLabel("E-mail").fill(email);
  await page.getByRole("button", { name: "Enviar instruções" }).click();
  await expect(page.getByText("Se o e-mail estiver cadastrado")).toBeVisible();

  // C2: o e-mail chega com o link para a tela de redefinição.
  const link = await lerLinkDeRedefinicao(email);
  expect(link.startsWith(`${URL_FRONT}/redefinir-senha?token=`)).toBe(true);

  // Ao abrir o link: o token some da barra de endereço e o navegador é
  // instruído a não repassar a URL para outros sites.
  const resposta = await page.goto(link);
  expect(resposta?.headers()["referrer-policy"]).toBe("no-referrer");
  await expect(page.getByLabel("Nova senha", { exact: true })).toBeVisible();
  await expect(page).toHaveURL(`${URL_FRONT}/redefinir-senha`);

  // C3: define a nova senha e consegue entrar com ela.
  await salvarNovaSenha(page, NOVA_SENHA);
  await expect(page.getByText("Senha redefinida com sucesso")).toBeVisible();
  await page.getByRole("link", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/login$/);

  await entrar(page, email, NOVA_SENHA);
  await expect(page.getByText(`Você entrou como ${nome}.`)).toBeVisible();

  // A senha antiga não funciona mais.
  await entrar(page, email, senhaAntiga);
  await expect(page.getByText("E-mail ou senha incorretos.")).toBeVisible();
});

test("link já usado mostra mensagem clara e oferece pedir outro", async ({ page, request }) => {
  const { email } = USUARIOS.linkJaUsado;
  await esvaziarCaixa(email);

  // Prepara pela API: pede o link e o usa uma vez.
  await request.post(`${URL_API}/api/v1/auth/esqueci-senha`, { data: { email } });
  const link = await lerLinkDeRedefinicao(email);
  const token = new URL(link).searchParams.get("token");
  const primeiroUso = await request.post(`${URL_API}/api/v1/auth/redefinir-senha`, {
    data: { token, nova_senha: NOVA_SENHA },
  });
  expect(primeiroUso.ok()).toBe(true);

  // C4: abrir o mesmo link de novo e tentar usar.
  await page.goto(link);
  await salvarNovaSenha(page, "OutraSenha789");

  await expect(
    page.getByText("Este link já foi usado. Se precisar, peça um novo link."),
  ).toBeVisible();
  await expect(page.getByLabel("Nova senha", { exact: true })).toBeHidden();
  await page.getByRole("link", { name: "Pedir novo link" }).click();
  await expect(page).toHaveURL(/\/esqueci-senha$/);
  await expect(page.getByLabel("E-mail")).toBeVisible();
});
