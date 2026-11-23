import type { Metadata } from "next";

import { CartaoAutenticacao } from "@/components/cartao-autenticacao";
import { FormEsqueciSenha } from "@/features/recuperacao-senha/form-esqueci-senha";

export const metadata: Metadata = { title: "Esqueci minha senha" };

export default function PaginaEsqueciSenha() {
  return (
    <CartaoAutenticacao
      titulo="Esqueci minha senha"
      descricao="Informe o e-mail da sua conta. Enviaremos um link para você criar uma nova senha."
    >
      <FormEsqueciSenha />
    </CartaoAutenticacao>
  );
}
