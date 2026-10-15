import { it, expect } from 'vitest'
import { render, fireEvent, within } from '@testing-library/react'
import MarkdownRenderer from '../components/MarkdownRenderer'
import fixture from './fixtures/blockedLinkOneOne.json'
import { expectCardListsHostRecords } from './blockedLinkCardAsserts'
import { i18nT } from '../i18n/t'

// Backend output of TestBlockedLinkCardRecords._one_presigned_one_key_split_flush
// (test/test_chat_runner_coverage.py), byte for byte: ONE presigned S3 link
// split at &X-Amz-Date (a placeholder with no record of its own) beside ONE
// same-host URL whose key a delta redacted (a placeholder with the one record).
// Two placeholders and one record, of different addresses. Each chip names
// the host alone: one record on the host does not prove it is a chip's link.
// The card lists that record under its own address and never presents it as
// the report.csv link the first chip stands for.
it('two placeholders and one record of different addresses: the record shows its own address, not as the clicked link', () => {
  const { getAllByTestId, getByTestId } = render(
    <MarkdownRenderer content={fixture.content} blockedLinks={fixture.blocked_links} slotKey="s1" />)
  expect(getAllByTestId('blocked-link-inspect')).toHaveLength(2)
  const host = fixture.blocked_links[0].domain
  fireEvent.click(getAllByTestId('blocked-link-inspect')[0])
  expectCardListsHostRecords(getByTestId('blocked-link-card'), fixture.blocked_links, host)
  expect(getByTestId('blocked-link-card').textContent).not.toContain('report.csv')
})

it('chip labels do not name a record as the removed link', () => {
  const { getAllByTestId } = render(
    <MarkdownRenderer content={fixture.content} blockedLinks={fixture.blocked_links} slotKey="s1" />)
  const chips = getAllByTestId('blocked-link-chip')
  expect(chips).toHaveLength(2)
  const rec = fixture.blocked_links[0]
  for (const chip of chips) {
    expect(within(chip).getByTestId('blocked-link-target').textContent).toBe(rec.domain)
    expect(chip.textContent).not.toContain(rec.path)
    expect(within(chip).queryByTestId('blocked-link-query')).toBeNull()
  }
})

it('the lone record is listed under its own address, with no claim that it is the clicked link', () => {
  // Nothing proves the one record is a chip's link, so the card frames it
  // the way it frames several: a blocked link to this host, under its own
  // address, below a title that never says "this link".
  const { getAllByTestId, getByTestId } = render(
    <MarkdownRenderer content={fixture.content} blockedLinks={fixture.blocked_links} slotKey="s1" />)
  fireEvent.click(getAllByTestId('blocked-link-inspect')[0])
  const card = getByTestId('blocked-link-card')
  const rec = fixture.blocked_links[0]
  expect(within(card).getByTestId('blocked-link-entry-target').textContent).toBe(`${rec.domain}${rec.path}`)
  expect(card.textContent).toContain(i18nT('components.redaction.link_title_host'))
  expect(card.textContent).not.toMatch(/this link/i)
  // The record kept no address (a credential), so the card offers no way to open it.
  expect(within(card).queryByTestId('blocked-link-review')).toBeNull()
  expect(within(card).queryByTestId('blocked-link-open-once')).toBeNull()
  expect(within(card).getByTestId('blocked-link-withheld')).toBeTruthy()
})

it('the saved text holds none of either link\'s query', () => {
  const { container, getAllByTestId, getByTestId } = render(
    <MarkdownRenderer content={fixture.content} blockedLinks={fixture.blocked_links} slotKey="s1" />)
  const text = container.textContent ?? ''
  expect(text).not.toContain('X-Amz-')
  expect(text).not.toContain('a'.repeat(64))
  for (const a of Array.from(container.querySelectorAll('a'))) expect(a.textContent).not.toContain('X-Amz')
  fireEvent.click(getAllByTestId('blocked-link-inspect')[0])
  expect(getByTestId('blocked-link-card').textContent).not.toContain('X-Amz')
})
