import { describe, it, expect } from 'vitest'
import { ExcludeIncludeLabelPrompt } from '@/components/types.d'

// ──────────────────────────────────────────────────────────
// ExcludeIncludeLabelPrompt enum
// ──────────────────────────────────────────────────────────
describe('ExcludeIncludeLabelPrompt', () => {
  /**
   * This enum is the only runtime artifact from types.d.ts.
   * helpers.ts uses `Number(excludeIncludeLabelPrompt[event.shape])` (line 291)
   * to resolve point labels — wrong values here silently break include/exclude logic.
   */

  it('ExcludeMarkerPrompt equals 0', () => {
    expect(ExcludeIncludeLabelPrompt.ExcludeMarkerPrompt).toBe(0)
  })

  it('IncludeMarkerPrompt equals 1', () => {
    expect(ExcludeIncludeLabelPrompt.IncludeMarkerPrompt).toBe(1)
  })

  it('has exactly 2 members', () => {
    /**
     * TypeScript numeric enums produce reverse mappings (value → name),
     * so Object.keys contains both names and numeric keys: ["0", "1", "ExcludeMarkerPrompt", "IncludeMarkerPrompt"].
     * We filter to non-numeric keys to count actual members.
     */
    const members = Object.keys(ExcludeIncludeLabelPrompt).filter((k) => isNaN(Number(k)))
    expect(members).toHaveLength(2)
  })

  /** helpers.ts relies on reverse mapping: enum[shapeName] → numeric label */
  it('reverse mapping: 0 resolves to "ExcludeMarkerPrompt"', () => {
    expect(ExcludeIncludeLabelPrompt[0]).toBe('ExcludeMarkerPrompt')
  })

  it('reverse mapping: 1 resolves to "IncludeMarkerPrompt"', () => {
    expect(ExcludeIncludeLabelPrompt[1]).toBe('IncludeMarkerPrompt')
  })
})
