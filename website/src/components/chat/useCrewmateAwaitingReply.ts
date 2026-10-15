import { useCallback, useEffect, useRef, useState } from 'react'
import type { ChatMessage } from '../../types'
import { awaitingCrewmateReply } from './crewmateBubbles'
import type { PillActivity } from '../../pages/members/pillActivity'

/** The caption while a send waits for the turn that will answer it: the
 *  pill's own `working` phase (no new wording), never the slot's status record,
 *  which still names the last turn's step. */
export const AWAITING_REPLY_ACTIVITY: PillActivity = { kind: 'working' }

/**
 * Whether a crewmate chat's newest send from this pane still waits for the
 * crewmate, so the typing bubble shows from the moment the person presses
 * Send rather than only once the turn that answers has started
 * (`awaitingCrewmateReply` is the row rule).
 *
 * `markSent` records the send; it is bound to the slot it was typed into, so a
 * pane rebound to another crewmate waits on nothing. A live turn that ends
 * while the send is NOT parked in the queue ends the wait too: that turn was
 * the one that took the send and it wrote no row for it. A turn that ends while
 * the send is still queued is the one before it, so the wait goes on.
 */
export function useCrewmateAwaitingReply(
  enabled: boolean,
  slotKey: string,
  all: ChatMessage[],
  live: boolean,
): { awaitingReply: boolean; markSent: (sendId: string) => void } {
  const [awaited, setAwaited] = useState<{ slot: string; sendId: string } | null>(null)
  const wasLive = useRef(live)
  useEffect(() => {
    const fell = wasLive.current && !live
    wasLive.current = live
    if (!fell || !awaited) return
    if (!all.some(m => m.role === 'queued' && m.meta?.sendId === awaited.sendId)) setAwaited(null)
  }, [live, awaited, all])
  const markSent = useCallback((sendId: string) => setAwaited({ slot: slotKey, sendId }), [slotKey])
  const awaitingReply = enabled && awaited?.slot === slotKey && awaitingCrewmateReply(all, awaited.sendId)
  return { awaitingReply, markSent }
}
