// PROVISÓRIO: substituir pela implementação da issue [1.1]
"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { CampoFormulario } from "@/components/campo-formulario";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";
import { enviarParaApi } from "@/lib/api/cliente";

const esquemaLogin = z.object({
  email: z
    .string()
    .trim()
    .pipe(z.email({ error: "Informe um e-mail válido." })),
  senha: z.string().min(1, { error: "Informe sua senha." }),
});
type DadosLogin = z.infer<typeof esquemaLogin>;
type UsuarioLogado = { id: number; nome: string; email: string; papel: string };

export function FormLogin() {
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const formulario = useForm<DadosLogin>({
    resolver: zodResolver(esquemaLogin),
    defaultValues: { email: "", senha: "" },
  });
  const login = useMutation({
    mutationFn: (dados: DadosLogin) => enviarParaApi<UsuarioLogado>("/api/v1/auth/login", dados),
  });

  if (login.isSuccess) {
    // Provisório: o redirecionamento por perfil é da issue [1.1]/[1.3].
    return (
      <Alert>
        <AlertDescription>Você entrou como {login.data.nome}.</AlertDescription>
      </Alert>
    );
  }

  const erros = formulario.formState.errors;
  return (
    <form
      noValidate
      className="grid gap-4"
      onSubmit={formulario.handleSubmit((dados) => login.mutate(dados))}
    >
      <CampoFormulario
        id="email"
        rotulo="E-mail"
        type="email"
        autoComplete="email"
        erro={erros.email?.message}
        {...formulario.register("email")}
      />
      <CampoFormulario
        id="senha"
        rotulo="Senha"
        type={mostrarSenha ? "text" : "password"}
        autoComplete="current-password"
        erro={erros.senha?.message}
        acessorio={
          <Button type="button" variant="outline" onClick={() => setMostrarSenha((v) => !v)}>
            {mostrarSenha ? "Ocultar" : "Mostrar"}
          </Button>
        }
        {...formulario.register("senha")}
      />

      {login.isError && (
        <Alert variant="destructive">
          <AlertDescription>{login.error.message}</AlertDescription>
        </Alert>
      )}

      <Button type="submit" disabled={login.isPending}>
        {login.isPending ? "Entrando..." : "Entrar"}
      </Button>
      <Link href="/esqueci-senha" className={buttonVariants({ variant: "link" })}>
        Esqueci minha senha
      </Link>
    </form>
  );
}
