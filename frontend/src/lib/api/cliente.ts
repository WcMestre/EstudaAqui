// PROVISÓRIO: substituir pela implementação da issue [0.3]
/**
 * Cliente HTTP único para falar com a API.
 *
 * - Envia e recebe JSON.
 * - `credentials: "include"` faz o navegador mandar o cookie de sessão.
 * - Qualquer erro vira um `ErroApi` com `codigo` e `mensagem` em português,
 *   no mesmo formato que o back-end usa: {"codigo": "...", "mensagem": "..."}.
 */

export const URL_DA_API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ErroApi extends Error {
  constructor(
    readonly status: number,
    readonly codigo: string,
    mensagem: string,
  ) {
    super(mensagem);
    this.name = "ErroApi";
  }
}

type CorpoDeErro = { codigo?: unknown; mensagem?: unknown };

export async function enviarParaApi<Resposta>(caminho: string, corpo: unknown): Promise<Resposta> {
  let resposta: Response;
  try {
    resposta = await fetch(`${URL_DA_API}${caminho}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(corpo),
      credentials: "include",
    });
  } catch {
    throw new ErroApi(
      0,
      "sem_conexao",
      "Não foi possível falar com o servidor. Verifique sua conexão e tente de novo.",
    );
  }

  const dados: unknown = await resposta.json().catch(() => null);
  if (!resposta.ok) {
    const erro = (dados ?? {}) as CorpoDeErro;
    throw new ErroApi(
      resposta.status,
      typeof erro.codigo === "string" ? erro.codigo : "erro_inesperado",
      typeof erro.mensagem === "string"
        ? erro.mensagem
        : "Ocorreu um erro inesperado. Tente novamente.",
    );
  }
  return dados as Resposta;
}
