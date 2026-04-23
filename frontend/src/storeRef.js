/** Avoid import cycles: api interceptors can dispatch without importing `store` from `store/index.js`. */
let storeRef = null

export function setStore(store) {
  storeRef = store
}

export function getStore() {
  return storeRef
}
