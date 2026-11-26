"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";

import { CampoFormulario } from "@/components/campo-formulario";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";

import { linkFoiRecusado, redefinirSenha } from "./api";
import { esquemaRedefinirSenha, type DadosRedefinirSenha } from "./esquemas";

const MENSAGEM_SEM_TOKEN = "Este link de redefinição não é válido. Peça um novo link.";

type Token = { situacao: "lendo" } | { situacao: "ausente" } | { situacao: "lido"; valor: string };

/**
 * Lê o token da URL uma única vez e o apaga da barra de endereço.
 *
 * Assim o token não fica no histórico do navegador, não aparece num print
 * da tela e não vaza para outros sites (junto com Referrer-Policy:
 * no-referrer, configurado no next.config.ts).
 */
function useTokenDaUrl(): Token {
  const [token, setToken] = useState<Token>({ situacao: "lendo" });
  const jaLeu = useRef(false);

  useEffect(() => {
    // O efeito pode rodar mais de uma vez (modo estrito do React, ou ao
    // voltar para a página); na segunda vez a URL já não tem mais o token.
    if (jaLeu.current) return;
    jaLeu.current = true;

    const valor = new URLSearchParams(window.location.search).get("token");
    window.history.replaceState(null, "", window.location.pathname);
    // A URL só existe no navegador, então este estado só pode ser definido
    // depois de montar (no servidor a página é pré-renderizada sem URL).
    setToken(valor ? { situacao: "lido", valor } : { situacao: "ausente" });
  }, []);

  return token;
}

function OfertaDeNovoLink({ mensagem }: { mensagem: string }) {
  return (
    <div className="grid gap-4">
      <Alert variant="destructive">
        <AlertDescription>{mensagem}</AlertDescription>
      </Alert>
      <Link href="/esqueci-senha" className={buttonVariants()}>
        Pedir novo link
      </Link>
    </div>
  );
}

export function FormRedefinirSenha() {
  const token = useTokenDaUrl();
  const formulario = useForm<DadosRedefinirSenha>({
    resolver: zodResolver(esquemaRedefinirSenha),
    defaultValues: { novaSenha: "", confirmacao: "" },
  });
  const troca = useMutation({
    mutationFn: (dados: DadosRedefinirSenha & { token: string }) =>
      redefinirSenha(dados.token, dados.novaSenha),
  });

  if (token.situacao === "lendo") {
    return <p className="text-sm text-muted-foreground">Carregando...</p>;
  }
  if (token.situacao === "ausente") {
    return <OfertaDeNovoLink mensagem={MENSAGEM_SEM_TOKEN} />;
  }
  if (linkFoiRecusado(troca.error)) {
    return <OfertaDeNovoLink mensagem={troca.error.message} />;
  }
  if (troca.isSuccess) {
    return (
      <div className="grid gap-4">
        <Alert>
          <AlertDescription>{troca.data.mensagem}</AlertDescription>
        </Alert>
        <Link href="/login" className={buttonVariants()}>
          Entrar
        </Link>
      </div>
    );
  }

  const erros = formulario.formState.errors;
  return (
    <form
      noValidate
      className="grid gap-4"
      onSubmit={formulario.handleSubmit((dados) => troca.mutate({ ...dados, token: token.valor }))}
    >
      <CampoFormulario
        id="nova-senha"
        rotulo="Nova senha"
        type="password"
        autoComplete="new-password"
        erro={erros.novaSenha?.message}
        {...formulario.register("novaSenha")}
      />
      <CampoFormulario
        id="confirmacao"
        rotulo="Confirme a nova senha"
        type="password"
        autoComplete="new-password"
        erro={erros.confirmacao?.message}
        {...formulario.register("confirmacao")}
      />

      {troca.isError && (
        <Alert variant="destructive">
          <AlertDescription>{troca.error.message}</AlertDescription>
        </Alert>
      )}

      <Button type="submit" disabled={troca.isPending}>
        {troca.isPending ? "Salvando..." : "Salvar nova senha"}
      </Button>
    </form>
  );
}
