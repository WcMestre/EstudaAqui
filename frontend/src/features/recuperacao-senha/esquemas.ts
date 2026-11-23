/**
 * Regras dos formulários da recuperação de senha (Zod).
 *
 * São as mesmas regras do back-end (8 a 128 caracteres), repetidas aqui só
 * para dar retorno imediato ao usuário. Quem garante as regras é o back-end.
 */
import { z } from "zod";

export const TAMANHO_MINIMO_SENHA = 8;
export const TAMANHO_MAXIMO_SENHA = 128;

export const esquemaEsqueciSenha = z.object({
  email: z
    .string()
    .trim()
    .min(1, { error: "Informe seu e-mail." })
    .pipe(z.email({ error: "Informe um e-mail válido." })),
});

export const esquemaRedefinirSenha = z
  .object({
    novaSenha: z
      .string()
      .min(TAMANHO_MINIMO_SENHA, {
        error: `A nova senha deve ter pelo menos ${TAMANHO_MINIMO_SENHA} caracteres.`,
      })
      .max(TAMANHO_MAXIMO_SENHA, {
        error: `A nova senha deve ter no máximo ${TAMANHO_MAXIMO_SENHA} caracteres.`,
      }),
    confirmacao: z.string().min(1, { error: "Confirme a nova senha." }),
  })
  .refine((dados) => dados.novaSenha === dados.confirmacao, {
    error: "As senhas não conferem.",
    path: ["confirmacao"],
  });

export type DadosEsqueciSenha = z.infer<typeof esquemaEsqueciSenha>;
export type DadosRedefinirSenha = z.infer<typeof esquemaRedefinirSenha>;
