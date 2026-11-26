/** Chamadas à API da recuperação de senha. */
import { ErroApi, enviarParaApi } from "@/lib/api/cliente";

type RespostaMensagem = { mensagem: string };

export function pedirLinkDeRedefinicao(email: string) {
  return enviarParaApi<RespostaMensagem>("/api/v1/auth/esqueci-senha", { email });
}

export function redefinirSenha(token: string, novaSenha: string) {
  return enviarParaApi<RespostaMensagem>("/api/v1/auth/redefinir-senha", {
    token,
    nova_senha: novaSenha,
  });
}

/** Códigos que o back-end usa quando o link não serve mais. */
const CODIGOS_DE_LINK_RECUSADO = new Set(["link_invalido", "link_expirado", "link_ja_usado"]);

export function linkFoiRecusado(erro: unknown): erro is ErroApi {
  return erro instanceof ErroApi && CODIGOS_DE_LINK_RECUSADO.has(erro.codigo);
}
