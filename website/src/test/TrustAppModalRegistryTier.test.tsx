/**
 * The install consent gate says when the registry that listed an app is a
 * `community` one (#11159), and the credential clause of that sentence follows
 * the registry's `trust`, never its review tier. The tier is display only:
 * every existing consent line still renders, unchanged, at every tier.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, renderHook, screen, within } from '@testing-library/react'
import type { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'

// Render catalog KEYS, as the main trust-modal suite does, so this pins which
// sentence is chosen rather than its copywriting.
vi.mock('../i18n/t', () => ({
  i18nT: (key: string, vars?: Record<string, unknown>) =>
    vars && Object.keys(vars).length ? `${key} ${Object.values(vars).join(' ')}` : key,
}))

import TrustAppModal, { type TrustAppTarget } from '../components/appstore/TrustAppModal'
import { findSourceRow, registryTierFor } from '../components/appstore/registryTier'
import { useAppActions } from '../pages/apps/useAppActions'

const K = 'components.appstore.trustAppModal'
// The i18n mock appends the interpolated values after a space, so the trailing
// space keeps the free key from matching inside the credentialed one, and the
// app name after it proves the sentence names this one app.
const CREDENTIALED = `${'components.appstore.trustAppModal.registry_community_credentialed'} Third Party`
const CREDENTIAL_FREE = `${'components.appstore.trustAppModal.registry_community'} Third Party`
const NOT_VETTED = 'components.appstore.registryTier.community'

const BASE: TrustAppTarget = {
  name: 'third-party',
  displayName: 'Third Party',
  origin: 'registry',
  _registry: 'community',
  trustRepository: 'https://git.example.test/org/third-party',
  retryInstalls: true,
}

function renderModal(app: TrustAppTarget) {
  render(
    <TrustAppModal app={app} pending={false} failed={false} granted={false} onCancel={() => {}} onConfirm={() => {}} />,
  )
  return screen.getByRole('dialog')
}

/** The consent lines every tier must keep rendering, byte for byte. */
function expectConsentStepsIntact(dialog: HTMLElement) {
  const text = dialog.textContent ?? ''
  for (const key of [
    `${K}.scope`, `${K}.intro`, `${K}.capability_python`, `${K}.capability_backend`,
    `${K}.capability_shell`, `${K}.capability_note`, `${K}.source`, `${K}.not_reviewed`,
    `${K}.install_outcome`, `${K}.install_on_cancel`, `${K}.revocable`,
  ]) expect(text).toContain(key)
  expect(within(dialog).getByRole('button', { name: `${K}.confirm_install` })).toBeTruthy()
  expect(within(dialog).getByRole('button', { name: `${K}.cancel` })).toBeTruthy()
}

describe('registryTierFor', () => {
  const rows = [
    { name: 'community', review: 'community', trust: 'index' },
    { name: 'internal', review: 'curated', trust: 'owner' },
    { name: 'mine', trust: 'index' },
  ]

  it('resolves a community tag to its tier and trust', () => {
    expect(registryTierFor('community', rows)).toEqual({ registryReview: 'community', registryTrust: 'index' })
  })

  it('carries no claim for a curated registry: the gate adds no endorsement', () => {
    expect(registryTierFor('internal', rows)).toEqual({})
  })

  it('makes no claim for an untagged, unknown or unreviewed registry', () => {
    expect(registryTierFor(undefined, rows)).toEqual({})
    expect(registryTierFor('nope', rows)).toEqual({})
    expect(registryTierFor('mine', rows)).toEqual({})
    expect(registryTierFor('x', [{ name: 'x', review: 'bogus' }])).toEqual({})
  })

  it('lets the FIRST case-insensitive row win, and needs an exact id match', () => {
    // Pinned rows come first: a later operator row with the same id never
    // replaces the build's community tier.
    expect(registryTierFor('community', [
      { name: 'community', review: 'community', trust: 'index' },
      { name: 'Community' },
    ])).toEqual({ registryReview: 'community', registryTrust: 'index' })
    // A stale case-variant tag borrows nobody's claim.
    expect(registryTierFor('Community', rows)).toEqual({})
  })

  it('ignores built-in source rows', () => {
    expect(registryTierFor('community', [{ name: 'community', review: 'community', builtin: true }])).toEqual({})
  })

  it('finds the row AppSource labels, by the same rule', () => {
    const pinned = { name: 'community', label: 'Community apps' }
    expect(findSourceRow('community', [pinned, { name: 'Community', label: 'Operator copy' }])).toBe(pinned)
    expect(findSourceRow('Community', [pinned])).toBeUndefined()
    expect(findSourceRow(undefined, [pinned])).toBeUndefined()
  })
})

describe('TrustAppModal registry tier', () => {
  it('says a community listing was not vetted, with no Git credentials at the index tier', () => {
    const dialog = renderModal({ ...BASE, registryReview: 'community', registryTrust: 'index' })
    const box = within(dialog).getByTestId('trust-app-registry-community')
    expect(box.textContent).toContain(NOT_VETTED)
    expect(box.textContent).toContain(CREDENTIAL_FREE)
    // The not-an-endorsement line stays next to the source badge; the box follows it.
    const notReviewed = within(dialog).getByText(`${K}.not_reviewed`)
    expect(notReviewed.compareDocumentPosition(box) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(box.textContent).not.toContain(CREDENTIALED)
    expectConsentStepsIntact(dialog)
  })

  it('names the Git credentials only when the registry clones with them', () => {
    const dialog = renderModal({ ...BASE, registryReview: 'community', registryTrust: 'owner' })
    const box = within(dialog).getByTestId('trust-app-registry-community')
    expect(box.textContent).toContain(CREDENTIALED)
    expect(box.textContent).not.toContain(CREDENTIAL_FREE)
    expectConsentStepsIntact(dialog)
  })

  it('reads an unknown trust as credential-free copy, never the credentialed sentence', () => {
    const dialog = renderModal({ ...BASE, registryReview: 'community' })
    expect(dialog.textContent).toContain(CREDENTIAL_FREE)
    expect(dialog.textContent).not.toContain(CREDENTIALED)
  })

  it('renders exactly as before when the registry has no review tier', () => {
    const dialog = renderModal(BASE)
    expect(within(dialog).queryByTestId('trust-app-registry-community')).toBeNull()
    expect(dialog.textContent).not.toContain(NOT_VETTED)
    expectConsentStepsIntact(dialog)
  })
})

describe('useAppActions trust target tier', () => {
  const sources = [{ name: 'community', label: 'Community', count: 1, builtin: false, review: 'community', trust: 'index' }]
  const row = { name: 'third-party', displayName: 'Third Party', origin: 'registry', _registry: 'community' }
  const installed = (origin: string) => ({
    name: 'third-party', displayName: 'Third Party', origin, trustRepository: BASE.trustRepository,
    manifest: { permissions: {} },
  })

  /** `origin` null: nothing installed, the Discover path's not-installed row. */
  function targetFor(origin: string | null) {
    const qc = new QueryClient()
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={qc}><MemoryRouter>{children}</MemoryRouter></QueryClientProvider>
    )
    const { result } = renderHook(() => useAppActions({
      // The hook reads only these fields of each row.
      apps: (origin === null ? [] : [installed(origin)]) as never,
      browseApps: [row] as never,
      appsError: null, registryError: null, announceAppsChanged: () => {}, sources,
    }), { wrapper })
    return result.current.trustTarget('third-party')
  }

  it('carries the community tier for an app installed from that registry', () => {
    expect(targetFor('registry')).toMatchObject({ registryReview: 'community', registryTrust: 'index' })
  })

  it('carries no tier for a LOCAL install that shares a registry row name', () => {
    expect(targetFor('local').registryReview).toBeUndefined()
  })

  // The source badge and the not-vetted box must name the same registry, or
  // the gate shows a first-party label beside a community warning (#20656).
  it.each([
    ['Discover install (not installed)', null],
    ['Library enable (installed)', 'registry'],
  ])('names the same registry in the badge and the box on the %s path', (_path, origin) => {
    const target = targetFor(origin)
    expect(target).toMatchObject({ _registry: 'community', registryReview: 'community' })
    renderModal({ ...BASE, ...target })
    const dialog = screen.getByRole('dialog')
    expect(within(dialog).getByText('community')).toBeTruthy()
    expect(within(dialog).queryByText('components.appstore.types.kirocrew_registry')).toBeNull()
    expect(within(dialog).getByTestId('trust-app-registry-community')).toBeTruthy()
  })
})
