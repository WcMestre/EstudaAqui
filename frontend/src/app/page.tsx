// PROVISÓRIO: substituir pela implementação da issue [0.3]
import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";

export default function PaginaInicial() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-4 p-6">
      <h1 className="text-2xl font-semibold">EstudaAqui</h1>
      <Link href="/login" className={buttonVariants()}>
        Entrar
      </Link>
    </main>
  );
}
