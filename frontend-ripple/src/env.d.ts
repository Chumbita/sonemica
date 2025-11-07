/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE: string;  // URL base del backend mock o real
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
