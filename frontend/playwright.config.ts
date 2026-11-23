/**
 * Teste ponta a ponta: navegador de verdade + API + banco + Mailpit.
 *
 * Usa portas e banco próprios (3001, 8001 e estudaaqui_e2e) para nunca
 * misturar com o ambiente de desenvolvimento (3000, 8000 e estudaaqui).
 * Pré-requisitos: `docker compose up -d` (Postgres e Mailpit) e `uv` no PATH.
 */
import { randomBytes } from "node:crypto";

import { defineConfig, devices } from "@playwright/test";

import { URL_API, URL_BANCO_E2E, URL_FRONT } from "./e2e/enderecos";

export default defineConfig({
  testDir: "./e2e",
  testMatch: "**/*.spec.ts",
  globalSetup: "./e2e/preparacao-global.ts",
  // Os testes compartilham o banco e a caixa do Mailpit: um de cada vez.
  workers: 1,
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: URL_FRONT,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      name: "API",
      command: "uv run uvicorn app.main:app --port 8001",
      cwd: "../backend",
      url: `${URL_API}/docs`,
      reuseExistingServer: false,
      env: {
        DATABASE_URL: URL_BANCO_E2E,
        FRONTEND_URL: URL_FRONT,
        JWT_SEGREDO: randomBytes(32).toString("hex"),
        EMAIL_SUPRIMIR_ENVIO: "false",
      },
    },
    {
      name: "Front",
      command: "npm run build && npm run start -- -p 3001",
      url: URL_FRONT,
      timeout: 180_000,
      reuseExistingServer: false,
      env: { NEXT_PUBLIC_API_URL: URL_API },
    },
  ],
});
