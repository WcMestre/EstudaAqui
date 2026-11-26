// PROVISÓRIO: substituir pela implementação da issue [0.3]
import type { ComponentProps, ReactNode } from "react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type Props = ComponentProps<"input"> & {
  id: string;
  rotulo: string;
  erro?: string;
  /** Conteúdo extra ao lado do campo (ex.: botão "Mostrar"). */
  acessorio?: ReactNode;
};

/**
 * Rótulo + campo + mensagem de erro, ligados para leitores de tela:
 * aria-invalid marca o campo com erro e aria-describedby aponta para a
 * mensagem, que é lida junto com o rótulo.
 */
export function CampoFormulario({ id, rotulo, erro, acessorio, ...props }: Props) {
  const idErro = `${id}-erro`;
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{rotulo}</Label>
      <div className="flex gap-2">
        <Input
          id={id}
          aria-invalid={erro ? true : undefined}
          aria-describedby={erro ? idErro : undefined}
          {...props}
        />
        {acessorio}
      </div>
      {erro && (
        <p id={idErro} className="text-sm text-destructive">
          {erro}
        </p>
      )}
    </div>
  );
}
