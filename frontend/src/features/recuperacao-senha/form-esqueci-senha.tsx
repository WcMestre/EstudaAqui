"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useForm } from "react-hook-form";

import { CampoFormulario } from "@/components/campo-formulario";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";

import { pedirLinkDeRedefinicao } from "./api";
import { esquemaEsqueciSenha, type DadosEsqueciSenha } from "./esquemas";

export function FormEsqueciSenha() {
  const formulario = useForm<DadosEsqueciSenha>({
    resolver: zodResolver(esquemaEsqueciSenha),
    defaultValues: { email: "" },
  });
  const pedido = useMutation({
    mutationFn: (dados: DadosEsqueciSenha) => pedirLinkDeRedefinicao(dados.email),
  });

  const voltarParaLogin = (
    <Link href="/login" className={buttonVariants({ variant: "link" })}>
      Voltar para o login
    </Link>
  );

  if (pedido.isSuccess) {
    // A mensagem é sempre a mesma, exista o e-mail ou não (vem da API).
    return (
      <div className="grid gap-4">
        <Alert>
          <AlertDescription>{pedido.data.mensagem}</AlertDescription>
        </Alert>
        {voltarParaLogin}
      </div>
    );
  }

  return (
    <form
      noValidate
      className="grid gap-4"
      onSubmit={formulario.handleSubmit((dados) => pedido.mutate(dados))}
    >
      <CampoFormulario
        id="email"
        rotulo="E-mail"
        type="email"
        autoComplete="email"
        erro={formulario.formState.errors.email?.message}
        {...formulario.register("email")}
      />

      {pedido.isError && (
        <Alert variant="destructive">
          <AlertDescription>{pedido.error.message}</AlertDescription>
        </Alert>
      )}

      <Button type="submit" disabled={pedido.isPending}>
        {pedido.isPending ? "Enviando..." : "Enviar instruções"}
      </Button>
      {voltarParaLogin}
    </form>
  );
}
