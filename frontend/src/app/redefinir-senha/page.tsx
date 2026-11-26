import type { Metadata } from "next";

import { CartaoAutenticacao } from "@/components/cartao-autenticacao";
import { FormRedefinirSenha } from "@/features/recuperacao-senha/form-redefinir-senha";

export const metadata: Metadata = {
  title: "Redefinir senha",
  // Além do cabeçalho HTTP (next.config.ts), a meta tag reforça que o
  // navegador não envie esta URL (com o token) para outros sites.
  referrer: "no-referrer",
};

export default function PaginaRedefinirSenha() {
  return (
    <CartaoAutenticacao
      titulo="Criar nova senha"
      descricao="Escolha uma senha com pelo menos 8 caracteres."
    >
      <FormRedefinirSenha />
    </CartaoAutenticacao>
  );
}
