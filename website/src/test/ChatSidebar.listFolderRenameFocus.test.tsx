/**
 * #13598 — ChatSidebar list-view folder rename: Enter and Escape restore focus
 * to the folder header row; a pointer blur moves nothing.
 *
 * Follows the pattern established by ChatSidebarW3Coverage.test.tsx:
 *  – framer-motion stubbed to plain DOM elements (same as W3Coverage)
 *  – @dnd-kit NOT mocked — the real library works in happy-dom
 *  – staleTime:Infinity + refetchOnMount:false prevent mid-test refetch races
 *  – Folder menu opened synchronously with keyboard Enter (the Radix path)
 *    then the rename item clicked in the SAME tick (no await in between),
 *    because Radix tears the dropdown down on the first macrotask
 *  – rename field located by role ('textbox' with no placeholder)
 *
 * All focus assertions run against the REAL [data-folder-row] element from
 * folderBlocks.tsx after the real `requestAnimationFrame(focusListFolderRow)`
 * fires.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { createTestStore } from './helpers'
import { ThemeProvider } from '../hooks/useTheme'
import type { RootState } from '../store'
import type { ChatFolder } from '../types'

// framer-motion: substitute real DOM tags so projection (which happy-dom cannot
// run) never fires, while preserving event wiring.  Same implementation as the
// sibling W3Coverage suite — the cache must produce a STABLE component type
// per tag so React does not unmount and remount on every render (which would
// detach focused elements).
vi.mock('framer-motion', async () => {
  const React = await import('react')
  const FRAMER_PROPS = new Set([
    'layout', 'layoutId', 'layoutScroll', 'initial', 'animate', 'exit',
    'transition', 'variants', 'whileHover', 'whileTap', 'whileInView',
    'drag', 'dragConstraints', 'dragElastic', 'onAnimationComplete',
  ])
  const cache = new Map<string, ReturnType<typeof React.forwardRef>>()
  const make = (tag: string) => {
    if (!cache.has(tag)) {
      cache.set(tag, React.forwardRef((props: Record<string, unknown>, ref: React.Ref<unknown>) => {
        const clean: Record<string, unknown> = {}
        for (const k of Object.keys(props)) {
          if (k === 'children') continue
          if (k === 'layoutId') { clean['data-layout-id'] = props[k]; continue }
          if (FRAMER_PROPS.has(k)) continue
          clean[k] = props[k]
        }
        return React.createElement(tag, { ...clean, ref }, props.children as React.ReactNode)
      }))
    }
    return cache.get(tag)!
  }
  const motion = new Proxy({}, { get: (_t, tag: string) => make(tag) })
  return {
    motion,
    AnimatePresence: ({ children }: { children?: React.ReactNode }) =>
      React.createElement(React.Fragment, null, children),
    LayoutGroup: ({ children }: { children?: React.ReactNode }) =>
      React.createElement(React.Fragment, null, children),
  }
})

vi.mock('../components/ProjectPicker', () => ({ default: () => null }))
// FolderConfigModal: minimal stub so any accidental open path renders nothing.
vi.mock('../components/FolderConfigModal', () => ({ default: () => null }))

vi.mock('../pages/chat/ChatSettings', () => ({
  loadChatConfig: () => ({ tagColumnsEnabled: false, confirmCloseSession: false }),
  saveChatConfig: vi.fn(),
}))

const mocks = vi.hoisted(() => ({
  chatFolders: vi.fn(),
  updateChatFolder: vi.fn(),
}))
vi.mock('../api/client', () => ({
  SEARCH_MIN_CHARS: 2,
  api: new Proxy(mocks as unknown as Record<string, unknown>, {
    get: (target, prop: string) =>
      (prop in target ? target[prop] : vi.fn().mockResolvedValue([])),
  }),
}))

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((q: string) => ({
    matches: false, media: q, onchange: null,
    addListener: vi.fn(), removeListener: vi.fn(),
    addEventListener: vi.fn(), removeEventListener: vi.fn(), dispatchEvent: vi.fn(),
  })),
})

// ── late imports ─────────────────────────────────────────────────────────────
import ChatSidebar from '../pages/ChatSidebar'

const FOLDER_ID = 'folder-rename-focus-13598'
const FOLDER_NAME = 'List Rename Focus Folder'

const testFolder: ChatFolder = {
  id: FOLDER_ID, name: FOLDER_NAME, collapsed: false, parent_id: '', color: '', icon: '',
}
// A slot filed under the test folder so the folder body renders (non-empty folder
// renders a body; an empty one renders the "new chat" empty-state affordance —
// either works, but a filed slot keeps the structure closer to real use).
const filedSlot = {
  key: 'k-rename-focus', title: 'Filed Chat', running: false,
  messages: 1, folder_id: FOLDER_ID,
}

function renderSidebar() {
  const defaults = createTestStore().getState()
  const store = createTestStore({
    dashboard: {
      ...defaults.dashboard,
      status: {}, connected: true,
      slots: [filedSlot], approvalMode: 'normal',
      channelTrusted: false, refreshTrigger: 0, unreadSlots: [], updateProgress: null,
      slotsLoaded: true,
      subagentRunning: {}, subagentDetails: {}, subagentText: {},
      sessionDefaultColor: null, sessionColorsMode: 'tint',
      sessionColorsPalette: 'horizon', sessionColorsIntensity: 'clear',
    } as unknown as RootState['dashboard'],
    chat: {
      ...defaults.chat,
      activeSlot: null, slotStatusDetail: {}, subagents: {},
      slotActivity: {}, automations: {}, workflowRuns: {},
      subagentQueued: {}, slotHistory: [],
    } as unknown as RootState['chat'],
  })
  // staleTime:Infinity + refetchOnMount:false keep the seeded data authoritative
  // — an on-mount refetch resolving mid-test would re-render the folder rows
  // and could unmount an open menu underneath the assertions.
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: Infinity, refetchOnMount: false },
      mutations: { retry: false },
    },
  })
  qc.setQueryData(['chat-folders'], [testFolder])
  qc.setQueryData(['tag-columns'], [])
  qc.setQueryData(['chat-tags'], [])
  render(
    <QueryClientProvider client={qc}>
      <Provider store={store}>
        <ThemeProvider>
          <MemoryRouter>
            <ChatSidebar
              slots={[filedSlot] as never} activeSlot={null} unreadSlots={[]}
              history={[]} historyHasMore={false}
              defaultAgent="" installedAgents={[{ name: 'builder', source: 'builtin' }]}
            />
            <button type="button" data-testid="elsewhere">Elsewhere</button>
          </MemoryRouter>
        </ThemeProvider>
      </Provider>
    </QueryClientProvider>,
  )
}

const nextFrame = () => act(async () => { await new Promise(requestAnimationFrame) })

/**
 * Open the folder's ⋯ menu.  This is SYNCHRONOUS and callers MUST fire the
 * desired menu-item click in the same tick (no `await` between), because Radix
 * tears the dropdown down on the first macrotask.  The item's onClick still
 * runs and what it triggers (the rename field, mutations) outlives the menu.
 */
function openFolderMenu() {
  fireEvent.keyDown(screen.getByTestId(`folder-menu-${FOLDER_ID}`), { key: 'Enter' })
  // Confirm the menu opened before the caller fires the item click.
  expect(screen.getByTestId(`folder-settings-${FOLDER_ID}`)).toBeTruthy()
}

/**
 * The rename text field.  Re-read on every call because each keystroke
 * re-renders the sidebar and replaces this input's DOM node.
 * It is the only textbox in the sidebar with no placeholder attribute.
 */
function folderRenameField(): HTMLInputElement {
  const el = screen.getAllByRole('textbox').find(node => !node.getAttribute('placeholder'))
  if (!el) throw new Error('folder rename field is not mounted')
  return el as HTMLInputElement
}

/** Open the rename field via the ⋯ menu and wait one frame for the field to mount. */
async function openFolderRename() {
  openFolderMenu()
  // Drive the rename item in the same tick — no await between openFolderMenu and click.
  fireEvent.click(screen.getByTestId(`folder-rename-${FOLDER_ID}`))
  await nextFrame()
  return folderRenameField()
}

beforeEach(() => {
  localStorage.clear()
  mocks.chatFolders.mockResolvedValue([testFolder])
  mocks.updateChatFolder.mockResolvedValue({ ok: true })
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('ChatSidebar list folder rename — focus contract (#13598)', () => {
  it('[data-folder-row] is rendered and the rename field mounts after menu → Rename', async () => {
    renderSidebar()
    // The folder row must be present before we open rename.
    expect(screen.getByTestId(`folder-menu-${FOLDER_ID}`)).toBeTruthy()
    const input = await openFolderRename()
    expect(input).toBeTruthy()
    expect(document.activeElement).not.toBe(document.body)
  })

  it('Enter commits rename and restores focus to the real [data-folder-row] div', async () => {
    renderSidebar()
    const input = await openFolderRename()

    act(() => { input.focus() })
    act(() => { fireEvent.change(input, { target: { value: 'Renamed Folder' } }) })
    act(() => { fireEvent.keyDown(folderRenameField(), { key: 'Enter' }) })
    // folderBlocks.tsx: renameCommit + requestAnimationFrame(focusListFolderRow)
    await nextFrame()

    const folderRow = document.querySelector(`[data-folder-row="${FOLDER_ID}"]`) as HTMLElement
    expect(folderRow).toBeTruthy()
    expect(document.activeElement).toBe(folderRow)
    expect(document.activeElement).not.toBe(document.body)
  })

  it('Escape cancels rename and restores focus to the real [data-folder-row] div', async () => {
    renderSidebar()
    const input = await openFolderRename()

    act(() => { input.focus() })
    act(() => { fireEvent.keyDown(folderRenameField(), { key: 'Escape' }) })
    // folderBlocks.tsx: setEditingId(null) + requestAnimationFrame(focusListFolderRow)
    await nextFrame()

    const folderRow = document.querySelector(`[data-folder-row="${FOLDER_ID}"]`) as HTMLElement
    expect(folderRow).toBeTruthy()
    expect(document.activeElement).toBe(folderRow)
    expect(document.activeElement).not.toBe(document.body)
  })

  it('pointer blur (onBlur) commits but does NOT redirect focus to [data-folder-row]', async () => {
    renderSidebar()
    const input = await openFolderRename()
    const elsewhere = document.querySelector('[data-testid="elsewhere"]') as HTMLElement

    act(() => { input.focus() })
    // Moving focus away triggers onBlur → renameCommit, which does NOT call
    // requestAnimationFrame(focusListFolderRow). Focus stays on 'elsewhere'.
    act(() => { elsewhere.focus() })
    await nextFrame()

    const folderRow = document.querySelector(`[data-folder-row="${FOLDER_ID}"]`) as HTMLElement
    expect(document.activeElement).toBe(elsewhere)
    expect(document.activeElement).not.toBe(folderRow)
    expect(document.activeElement).not.toBe(document.body)
  })

  it('Enter: activeElement is the real [data-folder-row] from folderBlocks.tsx (not body)', async () => {
    renderSidebar()
    const input = await openFolderRename()

    act(() => { input.focus() })
    expect(document.activeElement).toBe(folderRenameField())
    expect(document.activeElement).not.toBe(document.body)

    act(() => { fireEvent.keyDown(folderRenameField(), { key: 'Enter' }) })
    await nextFrame()

    const folderRow = document.querySelector(`[data-folder-row="${FOLDER_ID}"]`) as HTMLElement
    expect(document.activeElement).toBe(folderRow)
  })

  it('Escape: activeElement is the real [data-folder-row] from folderBlocks.tsx (not body)', async () => {
    renderSidebar()
    const input = await openFolderRename()

    act(() => { input.focus() })
    expect(document.activeElement).toBe(folderRenameField())

    act(() => { fireEvent.keyDown(folderRenameField(), { key: 'Escape' }) })
    await nextFrame()

    const folderRow = document.querySelector(`[data-folder-row="${FOLDER_ID}"]`) as HTMLElement
    expect(document.activeElement).toBe(folderRow)
  })
})
