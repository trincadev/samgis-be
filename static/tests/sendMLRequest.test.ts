import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

/**
 * Tests for sendMLRequest (helpers.ts lines 43–73).
 *
 * sendMLRequest calls getGeoJSONRequest which calls fetch() internally.
 * We mock fetch globally (matching the pattern in helpers.test.ts) so we
 * control what getGeoJSONRequest returns without partially mocking the module.
 *
 * Leaflet's geoJSON() and FeatureGroup are used on the success path.
 * We mock leaflet (same style as PagePredictionMap.test.ts) so those
 * constructors don't require a real DOM map.
 *
 * IMPORTANT: vi.mock is hoisted above imports, so the mock factory cannot
 * close over module-level variables that haven't been initialised yet.
 * We therefore define the mocks inside the factory using local variables,
 * and expose them via the module re-export so individual tests can import
 * the mocked functions and spy/assert on them after hoisting completes.
 */

vi.mock('leaflet', async () => {
  const actual = await vi.importActual('leaflet')
  return {
    ...actual,
    /**
     * geoJSON (aliased as LeafletGeoJSON in helpers.ts) is called as a
     * plain function: `const featureNew = LeafletGeoJSON(data)`.
     * It must return something that can be passed to map.addLayer()
     * and collected into a FeatureGroup array.
     */
    geoJSON: vi.fn(() => ({ _mock: 'geoJsonLayer' })),
    /**
     * FeatureGroup is used as `new FeatureGroup([...])` so its mock must
     * be a real constructor (class). We use a class so vitest doesn't warn
     * about non-constructor vi.fn() usage.
     */
    FeatureGroup: vi.fn(function(this: any, _layers: any[]) {
      this._mock = 'featureGroupInstance'
    }),
    icon: vi.fn(() => ({})),
  }
})

vi.mock('leaflet-providers', () => ({}))
vi.mock('@geoman-io/leaflet-geoman-free', () => ({}))

// Imports must come after vi.mock declarations (hoisting order is fine here).
import { sendMLRequest } from '@/components/helpers'
import {
  mapNavigationLocked,
  layerControlGroupLayersRef,
  waitingString,
  OpenStreetMap,
} from '@/components/constants'

// ──────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────

/**
 * Minimal mock Leaflet map satisfying the sendMLRequest surface.
 * getBounds() shape matches what getExtentCurrentViewMapBBox accesses.
 */
const makeMockMap = (opts?: { dragEnabled?: boolean; editEnabled?: boolean }) => ({
  pm: {
    globalDragModeEnabled: vi.fn(() => opts?.dragEnabled ?? false),
    globalEditModeEnabled: vi.fn(() => opts?.editEnabled ?? false),
    disableGlobalDragMode: vi.fn(),
    disableGlobalEditMode: vi.fn(),
  },
  getZoom: vi.fn(() => 10),
  getBounds: vi.fn(() => ({
    getNorthEast: () => ({ lat: 45, lng: 10 }),
    getSouthWest: () => ({ lat: 44, lng: 9 }),
  })),
  addLayer: vi.fn(),
})

const samplePrompts = [
  { id: 1, type: 'point' as const, data: { lat: 45, lng: 10 }, label: 1 },
]

/** Minimal valid GeoJSON response shaped as getGeoJSONRequest expects */
const validParsedOutput = {
  duration_run: 0.5,
  output: {
    geojson: '{"type":"FeatureCollection","features":[]}',
    n_predictions: 1,
    n_shapes_geojson: 1,
  },
}

const make200Response = (parsedOutput: object) => ({
  status: 200,
  json: () => Promise.resolve({ body: JSON.stringify(parsedOutput) }),
})

// ──────────────────────────────────────────────────────────
// T12: disables drag/edit modes and locks navigation
// ──────────────────────────────────────────────────────────
describe('T12: sendMLRequest disables drag/edit modes and locks navigation', () => {
  beforeEach(() => {
    mapNavigationLocked.value = false
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('disables drag mode when globalDragModeEnabled is true', async () => {
    const mockMap = makeMockMap({ dragEnabled: true, editEnabled: true })
    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('network error'))

    await sendMLRequest(mockMap as any, samplePrompts)

    expect(mockMap.pm.disableGlobalDragMode).toHaveBeenCalledTimes(1)
  })

  it('disables edit mode when globalEditModeEnabled is true', async () => {
    const mockMap = makeMockMap({ dragEnabled: true, editEnabled: true })
    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('network error'))

    await sendMLRequest(mockMap as any, samplePrompts)

    expect(mockMap.pm.disableGlobalEditMode).toHaveBeenCalledTimes(1)
  })

  it('sets mapNavigationLocked to true', async () => {
    const mockMap = makeMockMap({ dragEnabled: true, editEnabled: true })
    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('network error'))

    await sendMLRequest(mockMap as any, samplePrompts)

    expect(mapNavigationLocked.value).toBe(true)
  })
})

// ──────────────────────────────────────────────────────────
// T13: builds correct request body
// ──────────────────────────────────────────────────────────
describe('T13: sendMLRequest builds correct request body', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends fetch with bbox, prompt, zoom, and source_type', async () => {
    const mockMap = makeMockMap()
    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue(make200Response(validParsedOutput) as any)

    await sendMLRequest(mockMap as any, samplePrompts, OpenStreetMap)

    expect(fetchSpy).toHaveBeenCalledOnce()
    const [url, init] = fetchSpy.mock.calls[0]
    expect(url).toBe('/infer_samgis')

    const body = JSON.parse(init!.body as string)
    expect(body.bbox).toEqual({
      ne: { lat: 45, lng: 10 },
      sw: { lat: 44, lng: 9 },
    })
    expect(body.prompt).toEqual(samplePrompts)
    expect(body.zoom).toBe(10)
    expect(body.source_type).toBe(OpenStreetMap)
  })
})

// ──────────────────────────────────────────────────────────
// T14: success — adds GeoJSON layer to map and calls addOverlay
// ──────────────────────────────────────────────────────────
describe('T14: sendMLRequest success adds GeoJSON layer to map', () => {
  const mockAddOverlay = vi.fn()

  beforeEach(() => {
    mockAddOverlay.mockReset()
    layerControlGroupLayersRef.value = { addOverlay: mockAddOverlay } as any
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls leafletMap.addLayer with the geoJSON layer', async () => {
    const mockMap = makeMockMap()
    vi.spyOn(global, 'fetch').mockResolvedValue(make200Response(validParsedOutput) as any)

    await sendMLRequest(mockMap as any, samplePrompts)

    // geoJSON mock returns { _mock: 'geoJsonLayer' } — addLayer should receive it
    expect(mockMap.addLayer).toHaveBeenCalledTimes(1)
    const layerArg = mockMap.addLayer.mock.calls[0][0]
    expect(layerArg).toHaveProperty('_mock', 'geoJsonLayer')
  })

  it('calls layerControlGroupLayersRef.addOverlay with a FeatureGroup', async () => {
    const mockMap = makeMockMap()
    vi.spyOn(global, 'fetch').mockResolvedValue(make200Response(validParsedOutput) as any)

    await sendMLRequest(mockMap as any, samplePrompts)

    expect(mockAddOverlay).toHaveBeenCalledOnce()
    // Second arg is the locale timestamp string
    expect(typeof mockAddOverlay.mock.calls[0][1]).toBe('string')
    // First arg is a FeatureGroup instance constructed by the mock
    const overlayArg = mockAddOverlay.mock.calls[0][0]
    expect(overlayArg).toHaveProperty('_mock', 'featureGroupInstance')
  })
})

// ──────────────────────────────────────────────────────────
// T15: error — logs and does not throw
// ──────────────────────────────────────────────────────────
describe('T15: sendMLRequest error logs and does not throw', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('does not throw when fetch rejects', async () => {
    const mockMap = makeMockMap()
    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('network failure'))
    vi.spyOn(console, 'error').mockImplementation(() => {})

    await expect(sendMLRequest(mockMap as any, samplePrompts)).resolves.not.toThrow()
  })

  it('calls console.error at least once on fetch failure', async () => {
    const mockMap = makeMockMap()
    vi.spyOn(global, 'fetch').mockRejectedValue(new Error('network failure'))
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    await sendMLRequest(mockMap as any, samplePrompts)

    expect(errorSpy).toHaveBeenCalled()
  })
})

// ──────────────────────────────────────────────────────────
// T16: skips disable when drag/edit not enabled
// ──────────────────────────────────────────────────────────
describe('T16: sendMLRequest skips disable when drag/edit not enabled', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('does NOT call disableGlobalDragMode when drag mode is off', async () => {
    const mockMap = makeMockMap({ dragEnabled: false, editEnabled: false })
    vi.spyOn(global, 'fetch').mockResolvedValue(make200Response(validParsedOutput) as any)

    await sendMLRequest(mockMap as any, samplePrompts)

    expect(mockMap.pm.disableGlobalDragMode).not.toHaveBeenCalled()
  })

  it('does NOT call disableGlobalEditMode when edit mode is off', async () => {
    const mockMap = makeMockMap({ dragEnabled: false, editEnabled: false })
    vi.spyOn(global, 'fetch').mockResolvedValue(make200Response(validParsedOutput) as any)

    await sendMLRequest(mockMap as any, samplePrompts)

    expect(mockMap.pm.disableGlobalEditMode).not.toHaveBeenCalled()
  })
})
