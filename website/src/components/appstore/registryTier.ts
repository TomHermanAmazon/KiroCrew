/**
 * The registry row an app's `_registry` tag names, and the not-vetted claim the
 * install consent gate reads off it.
 *
 * `rows` must be in the backend's merge order (build-pinned rows first): on a
 * case-insensitive name collision the first row wins, the same rule
 * `_effective_registries` applies. A row is only returned when that winning
 * row's id matches the tag EXACTLY: a stale case-variant tag shows its own id
 * and borrows no other row's label or review claim. `AppSource` and the consent
 * gate both resolve through `findSourceRow`, so the rule lives here once.
 */
export type RegistryTierRow = { name: string; review?: string; trust?: string; builtin?: boolean }

export function findSourceRow<T extends RegistryTierRow>(registry: string | undefined, rows: readonly T[]): T | undefined {
  if (!registry) return undefined
  const key = registry.toLowerCase()
  const row = rows.find(r => !r.builtin && r.name.toLowerCase() === key)
  return row && row.name === registry ? row : undefined
}

/**
 * Only `community` is carried to the gate: it is the one tier that makes a
 * negative claim (the listing was not vetted). `trust` rides beside it because
 * the sentence names whether apps clone with the user's Git credentials, and
 * that fact is read from `trust`, never inferred from the review tier.
 */
export type RegistryTier = { registryReview?: 'community'; registryTrust?: string }

export function registryTierFor(registry: string | undefined, rows: readonly RegistryTierRow[]): RegistryTier {
  const row = findSourceRow(registry, rows)
  if (row?.review !== 'community') return {}
  return { registryReview: 'community', registryTrust: row.trust }
}
