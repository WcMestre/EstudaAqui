/**
 * Roda uma vez antes de todos os testes ponta a ponta:
 * confere se o Mailpit está no ar e recria o banco e2e com os usuários.
 */
import { execFileSync } from "node:child_process";
import path from "node:path";

import { URL_BANCO_E2E, URL_MAILPIT } from "./enderecos";
import { USUARIOS } from "./usuarios";

export default async function preparacaoGlobal() {
  try {
    await fetch(`${URL_MAILPIT}/api/v1/info`);
  } catch {
    throw new Error("Mailpit fora do ar. Rode `docker compose up -d` na raiz do projeto.");
  }

  execFileSync(
    "uv",
    ["run", "python", "scripts/preparar_banco_e2e.py", JSON.stringify(Object.values(USUARIOS))],
    {
      cwd: path.resolve(__dirname, "../../backend"),
      env: { ...process.env, DATABASE_URL: URL_BANCO_E2E },
      stdio: "inherit",
    },
  );
}
