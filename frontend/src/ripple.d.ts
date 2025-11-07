// src/ripple.d.ts
declare module "ripple" {
  /** Monta un componente raíz Ripple (similar a ReactDOM.render) */
  export function mount(component: any, options?: any): void;

  /** Crea una variable reactiva (similar a useState en React) */
  export function track<T>(initial: T): T;

  /** Ejecuta efectos cuando las dependencias cambian (similar a useEffect) */
  export function effect(fn: () => void): void;
}

/** Permite importar archivos .ripple como componentes */
declare module "*.ripple" {
  const component: any;
  export default component;
}
