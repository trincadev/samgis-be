import { describe, it, expect } from 'vitest'
import {
  prefix,
  OpenStreetMap,
  Satellite,
  maxZoom,
  minZoom,
  waitingString,
  durationRef,
  numberOfPolygonsRef,
  numberOfPredictedMasksRef,
  responseMessageRef,
  geojsonRef,
  currentBaseMapNameRef,
  currentMapBBoxRef,
  currentZoomRef,
  promptsArrayRef,
  mapOptionsDefaultRef,
  layerControlGroupLayersRef,
  mapNavigationLocked,
  htmlStatusMessages,
  driverSteps,
} from '@/components/constants'

// ──────────────────────────────────────────────────────────
// String and number constants
// ──────────────────────────────────────────────────────────
describe('string and number constants', () => {
  /**
   * These are contract guards: other modules (helpers.ts, components)
   * import these values and depend on their exact content.
   * A silent change here would break API requests or Leaflet config.
   */

  it('OpenStreetMap equals "OpenStreetMap" — used as source_type in API requests', () => {
    expect(OpenStreetMap).toBe('OpenStreetMap')
  })

  it('Satellite equals "OpenStreetMap.HOT" — used for basemap lookup', () => {
    expect(Satellite).toBe('OpenStreetMap.HOT')
  })

  it('maxZoom is 20', () => {
    expect(maxZoom).toBe(20)
  })

  it('minZoom is 2', () => {
    expect(minZoom).toBe(2)
  })

  it('waitingString equals "waiting..."', () => {
    expect(waitingString).toBe('waiting...')
  })

  /** Legal requirement: Leaflet attribution must be present. */
  it('prefix contains leaflet attribution link', () => {
    expect(prefix).toContain('leafletjs.com')
    expect(prefix).toContain('leaflet')
  })
})

// ──────────────────────────────────────────────────────────
// Vue refs initial values
// ──────────────────────────────────────────────────────────
describe('Vue refs initial values', () => {
  /**
   * Refs are module-scoped singletons. We only read .value here — no mutation.
   * These tests guard against accidental changes to defaults that
   * helpers.ts and components rely on (e.g., responseMessageRef starting at "-").
   */

  it('durationRef starts at 0', () => {
    expect(durationRef.value).toBe(0)
  })

  it('numberOfPolygonsRef starts at 0', () => {
    expect(numberOfPolygonsRef.value).toBe(0)
  })

  it('numberOfPredictedMasksRef starts at 0', () => {
    expect(numberOfPredictedMasksRef.value).toBe(0)
  })

  it('responseMessageRef starts at "-"', () => {
    expect(responseMessageRef.value).toBe('-')
  })

  it('geojsonRef starts at "geojsonOutput-placeholder"', () => {
    expect(geojsonRef.value).toBe('geojsonOutput-placeholder')
  })

  it('currentBaseMapNameRef starts at ""', () => {
    expect(currentBaseMapNameRef.value).toBe('')
  })

  it('promptsArrayRef starts as empty array', () => {
    expect(promptsArrayRef.value).toEqual([])
  })

  it('mapNavigationLocked starts as false', () => {
    expect(mapNavigationLocked.value).toBe(false)
  })

  it('currentMapBBoxRef starts as undefined', () => {
    expect(currentMapBBoxRef.value).toBeUndefined()
  })

  it('currentZoomRef starts as undefined', () => {
    expect(currentZoomRef.value).toBeUndefined()
  })

  it('mapOptionsDefaultRef starts as undefined', () => {
    expect(mapOptionsDefaultRef.value).toBeUndefined()
  })

  /**
   * layerControlGroupLayersRef wraps `new LeafletControl.Layers()`.
   * We only check it's truthy — asserting on Leaflet internals would
   * couple to their private API and break on Leaflet version bumps.
   */
  it('layerControlGroupLayersRef holds a truthy value', () => {
    expect(layerControlGroupLayersRef.value).toBeTruthy()
  })
})

// ──────────────────────────────────────────────────────────
// htmlStatusMessages
// ──────────────────────────────────────────────────────────
describe('htmlStatusMessages', () => {
  /**
   * Structural guards — not a full snapshot.
   * We check shape, count, uniqueness, and presence of critical codes
   * rather than asserting every phrase (too brittle for rewording).
   */

  it('has 55 entries', () => {
    expect(htmlStatusMessages).toHaveLength(55)
  })

  it('every entry has numeric code and string phrase', () => {
    for (const entry of htmlStatusMessages) {
      expect(typeof entry.code).toBe('number')
      expect(typeof entry.phrase).toBe('string')
      expect(entry.phrase.length).toBeGreaterThan(0)
    }
  })

  it('has no duplicate codes', () => {
    const codes = htmlStatusMessages.map((e) => e.code)
    expect(new Set(codes).size).toBe(codes.length)
  })

  it.each([
    [200, 'OK'],
    [400, 'Bad Request'],
    [404, 'Not Found'],
    [500, 'Internal Server Error'],
  ])('contains critical code %i with phrase "%s"', (code, phrase) => {
    const entry = htmlStatusMessages.find((e) => e.code === code)
    expect(entry).toBeDefined()
    expect(entry!.phrase).toBe(phrase)
  })
})

// ──────────────────────────────────────────────────────────
// driverSteps
// ──────────────────────────────────────────────────────────
describe('driverSteps', () => {
  /**
   * Tour steps target CSS selectors/IDs in the DOM.
   * A typo here silently breaks the onboarding tour with no error.
   * We guard structure + key entry points.
   */

  it('has 9 entries', () => {
    expect(driverSteps).toHaveLength(9)
  })

  it('every entry has element string and popover with title + description', () => {
    for (const step of driverSteps) {
      expect(typeof step.element).toBe('string')
      expect(step.element.length).toBeGreaterThan(0)
      expect(typeof step.popover.title).toBe('string')
      expect(typeof step.popover.description).toBe('string')
    }
  })

  it('first step targets "id-prediction-map-container" — tour entry point', () => {
    expect(driverSteps[0].element).toBe('id-prediction-map-container')
  })

  it('contains the submit button step', () => {
    const submitStep = driverSteps.find((s) => s.element === '#id-button-submit')
    expect(submitStep).toBeDefined()
  })
})
