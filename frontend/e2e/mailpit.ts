/** Leitura da caixa de e-mail do Mailpit pela API REST dele. */
import { expect } from "@playwright/test";

import { URL_MAILPIT } from "./enderecos";

type ResultadoBusca = { messages: { ID: string }[] };
type Mensagem = { Subject: string; Text: string };

const busca = (destinatario: string) =>
  `${URL_MAILPIT}/api/v1/search?query=${encodeURIComponent(`to:"${destinatario}"`)}`;

/** Apaga os e-mails já recebidos por este endereço (de execuções anteriores). */
export async function esvaziarCaixa(destinatario: string) {
  await fetch(busca(destinatario), { method: "DELETE" });
}

/** Espera chegar o e-mail de redefinição e devolve o link que está nele. */
export async function lerLinkDeRedefinicao(destinatario: string): Promise<string> {
  let ids: string[] = [];
  await expect
    .poll(
      async () => {
        const resposta = (await (await fetch(busca(destinatario))).json()) as ResultadoBusca;
        ids = resposta.messages.map((m) => m.ID);
        return ids.length;
      },
      { message: `o e-mail para ${destinatario} não chegou`, timeout: 10_000 },
    )
    .toBe(1);

  const mensagem = (await (
    await fetch(`${URL_MAILPIT}/api/v1/message/${ids[0]}`)
  ).json()) as Mensagem;
  expect(mensagem.Subject).toBe("Redefinição de senha - EstudaAqui");

  const link = mensagem.Text.match(/https?:\/\/\S+\/redefinir-senha\?token=[\w-]+/)?.[0];
  expect(link, "o e-mail não contém o link de redefinição").toBeTruthy();
  return link!;
}
