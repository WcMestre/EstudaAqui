/** Endereços do ambiente ponta a ponta (separados dos de desenvolvimento). */
export const URL_FRONT = "http://localhost:3001";
export const URL_API = "http://localhost:8001";
export const URL_MAILPIT = "http://localhost:8025";
export const URL_BANCO_E2E =
  process.env.DATABASE_URL_E2E ??
  "postgresql+psycopg://estudaaqui:estudaaqui@localhost:5432/estudaaqui_e2e";
