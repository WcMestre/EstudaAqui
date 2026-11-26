// PROVISÓRIO: substituir pela implementação da issue [1.1]
import type { Metadata } from "next";

import { CartaoAutenticacao } from "@/components/cartao-autenticacao";
import { FormLogin } from "@/features/autenticacao/form-login";

export const metadata: Metadata = { title: "Entrar" };

export default function PaginaLogin() {
  return (
    <CartaoAutenticacao titulo="Entrar" descricao="Use seu e-mail e sua senha.">
      <FormLogin />
    </CartaoAutenticacao>
  );
}
