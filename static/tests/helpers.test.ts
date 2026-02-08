import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import L from 'leaflet'
import {
  removeEventFromArrayByIndex,
  getCurrentBasemap,
  applyFnToObjectWithinArray,
  getSelectedPointCoordinate,
  getSelectedRectangleCoordinatesBBox,
  getPointPromptElement,
  getRectanglePromptElement,
  getExtentCurrentViewMapBBox,
  updateZoomBboxMap,
  getQueryParams,
  getGeoJSONRequest,
  getPopupContentPoint,
} from '@/components/helpers'
import {
  currentMapBBoxRef,
  currentZoomRef,
  responseMessageRef,
  durationRef,
  numberOfPolygonsRef,
  numberOfPredictedMasksRef,
  waitingString,
} from '@/components/constants'

/**
 * Leaflet's Evented class is declared as `abstract` in @types/leaflet (see node_modules/@types/leaflet/index.d.ts),
 * so it cannot be instantiated directly with `new Evented()`.
 * We use minimal plain objects that satisfy the shape the function actually accesses:
 * - array elements need `{ id }` (matched against the event's leaflet id)
 * - the event needs `{ layer: { _leaflet_id } }` (the internal Leaflet layer identifier)
 */
const makeElement = (id: number | string) => ({ id })
const makeEvent = (leafletId: number | string) => ({ layer: { _leaflet_id: leafletId } })

// ──────────────────────────────────────────────────────────
// removeEventFromArrayByIndex
// ──────────────────────────────────────────────────────────
describe('removeEventFromArrayByIndex', () => {
  it('removes the element matching e.layer._leaflet_id', () => {
    const arr = [makeElement(1), makeElement(2), makeElement(3)]
    const result = removeEventFromArrayByIndex(arr, makeEvent(2))
    expect(result).toEqual([makeElement(1), makeElement(3)])
  })

  it('returns array unchanged when no match found', () => {
    const arr = [makeElement(1), makeElement(2)]
    const result = removeEventFromArrayByIndex(arr, makeEvent(99))
    expect(result).toEqual([makeElement(1), makeElement(2)])
  })

  it('returns empty array when input is empty', () => {
    const result = removeEventFromArrayByIndex([], makeEvent(1))
    expect(result).toEqual([])
  })

  it('removes only the matching element among multiple', () => {
    const arr = [makeElement(10), makeElement(20), makeElement(30)]
    const result = removeEventFromArrayByIndex(arr, makeEvent(10))
    expect(result).toEqual([makeElement(20), makeElement(30)])
  })

  it('removes all elements with the same id', () => {
    const arr = [makeElement(5), makeElement(5), makeElement(6)]
    const result = removeEventFromArrayByIndex(arr, makeEvent(5))
    expect(result).toEqual([makeElement(6)])
  })

  it('does not match when types differ (strict equality)', () => {
    const arr = [makeElement(42)]
    const result = removeEventFromArrayByIndex(arr, makeEvent('42'))
    expect(result).toEqual([makeElement(42)])
  })

  it('does not mutate the original array', () => {
    const arr = [makeElement(1), makeElement(2)]
    const original = [...arr]
    removeEventFromArrayByIndex(arr, makeEvent(1))
    expect(arr).toEqual(original)
  })
})

// ──────────────────────────────────────────────────────────
// getCurrentBasemap
// ──────────────────────────────────────────────────────────
describe('getCurrentBasemap', () => {
  /**
   * `providersArray` mimics the ServiceTiles record: keys are provider names,
   * values are objects with a `_url` property (the internal Leaflet TileLayer URL).
   * We use plain objects instead of real TileLayer instances to avoid Leaflet DOM setup.
   */
  const providers = {
    OpenStreetMap: { _url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' },
    Satellite: { _url: 'https://server.arcgisonline.com/tile/{z}/{y}/{x}' },
  }

  it('returns matching key when URL found', () => {
    const result = getCurrentBasemap('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', providers)
    expect(result).toBe('OpenStreetMap')
  })

  it('returns second key when its URL matches', () => {
    const result = getCurrentBasemap('https://server.arcgisonline.com/tile/{z}/{y}/{x}', providers)
    expect(result).toBe('Satellite')
  })

  /** Fallback: "-" signals no basemap matched — consumer code can display a default label. */
  it('returns "-" when URL not found', () => {
    const result = getCurrentBasemap('https://unknown.url', providers)
    expect(result).toBe('-')
  })

  it('returns "-" for empty providers object', () => {
    const result = getCurrentBasemap('any-url', {})
    expect(result).toBe('-')
  })

  it('returns "-" for empty URL string', () => {
    const result = getCurrentBasemap('', providers)
    expect(result).toBe('-')
  })
})

// ──────────────────────────────────────────────────────────
// applyFnToObjectWithinArray
// ──────────────────────────────────────────────────────────
describe('applyFnToObjectWithinArray', () => {
  /**
   * This function dispatches to private getUpdatedPoint / getUpdatedRectangle
   * based on the `type` field. Testing it exercises both private functions
   * through the public API — no need to export them separately.
   */

  it('transforms a point prompt to IPointTable (drops type field)', () => {
    const point = { id: 1, type: 'point', data: { lat: 10, lng: 20 }, label: 1 }
    const result = applyFnToObjectWithinArray([point])
    expect(result).toEqual([{ id: 1, data: { lat: 10, lng: 20 }, label: 1 }])
  })

  it('transforms a rectangle prompt to IRectangleTable (flattens data)', () => {
    const ne = { lat: 45, lng: 10 }
    const sw = { lat: 44, lng: 9 }
    const rect = { id: 2, type: 'rectangle', data: { ne, sw } }
    const result = applyFnToObjectWithinArray([rect])
    expect(result).toEqual([{ id: 2, data_ne: ne, data_sw: sw }])
  })

  it('handles mixed array of points and rectangles', () => {
    const point = { id: 1, type: 'point', data: { lat: 10, lng: 20 }, label: 0 }
    const rect = { id: 2, type: 'rectangle', data: { ne: { lat: 45, lng: 10 }, sw: { lat: 44, lng: 9 } } }
    const result = applyFnToObjectWithinArray([point, rect])
    expect(result).toHaveLength(2)
    expect(result[0]).toEqual({ id: 1, data: { lat: 10, lng: 20 }, label: 0 })
    expect(result[1]).toEqual({ id: 2, data_ne: { lat: 45, lng: 10 }, data_sw: { lat: 44, lng: 9 } })
  })

  it('returns empty array for empty input', () => {
    expect(applyFnToObjectWithinArray([])).toEqual([])
  })

  it('does not mutate the original array', () => {
    const point = { id: 1, type: 'point', data: { lat: 10, lng: 20 }, label: 1 }
    const arr = [point]
    applyFnToObjectWithinArray(arr)
    expect(arr).toEqual([point])
  })
})

// ──────────────────────────────────────────────────────────
// getSelectedPointCoordinate
// ──────────────────────────────────────────────────────────
describe('getSelectedPointCoordinate', () => {
  /**
   * The function accesses `event.layer._latlng` — a Leaflet internal property.
   * We use a plain object with that shape rather than a real Marker instance.
   */

  it('returns the LatLng from the event layer', () => {
    const latlng = { lat: 45.5, lng: 9.2 }
    const event = { layer: { _latlng: latlng } }
    expect(getSelectedPointCoordinate(event)).toBe(latlng)
  })
})

// ──────────────────────────────────────────────────────────
// getSelectedRectangleCoordinatesBBox
// ──────────────────────────────────────────────────────────
describe('getSelectedRectangleCoordinatesBBox', () => {
  /**
   * Accesses `event.layer._bounds._northEast` and `_southWest`.
   * Returns BboxLatLng with real L.LatLng instances (via `new L.LatLng()`).
   * We assert on lat/lng values rather than strict object identity because
   * the function constructs new LatLng objects.
   */

  it('returns ne/sw as L.LatLng from event bounds', () => {
    const event = {
      layer: {
        _bounds: {
          _northEast: { lat: 46.0, lng: 11.0 },
          _southWest: { lat: 44.0, lng: 9.0 },
        },
      },
    }
    const result = getSelectedRectangleCoordinatesBBox(event)
    expect(result.ne.lat).toBe(46.0)
    expect(result.ne.lng).toBe(11.0)
    expect(result.sw.lat).toBe(44.0)
    expect(result.sw.lng).toBe(9.0)
  })

  /** Verify the returned objects are real L.LatLng instances, not plain objects. */
  it('returns L.LatLng instances (not plain objects)', () => {
    const event = {
      layer: {
        _bounds: {
          _northEast: { lat: 1, lng: 2 },
          _southWest: { lat: 3, lng: 4 },
        },
      },
    }
    const result = getSelectedRectangleCoordinatesBBox(event)
    expect(result.ne).toBeInstanceOf(L.LatLng)
    expect(result.sw).toBeInstanceOf(L.LatLng)
  })
})

// ──────────────────────────────────────────────────────────
// getPointPromptElement
// ──────────────────────────────────────────────────────────
describe('getPointPromptElement', () => {
  /**
   * Combines getSelectedPointCoordinate + prompt metadata.
   * The event mock needs both `layer._latlng` (for coord extraction)
   * and `layer._leaflet_id` (for the prompt id).
   */

  it('builds an include point prompt (label=1)', () => {
    const latlng = { lat: 45.0, lng: 9.0 }
    const event = { layer: { _latlng: latlng, _leaflet_id: 42 } }
    const result = getPointPromptElement(event, 1)
    expect(result).toEqual({ id: 42, type: 'point', data: latlng, label: 1 })
  })

  it('builds an exclude point prompt (label=0)', () => {
    const latlng = { lat: 44.0, lng: 8.0 }
    const event = { layer: { _latlng: latlng, _leaflet_id: 7 } }
    const result = getPointPromptElement(event, 0)
    expect(result).toEqual({ id: 7, type: 'point', data: latlng, label: 0 })
  })
})

// ──────────────────────────────────────────────────────────
// getRectanglePromptElement
// ──────────────────────────────────────────────────────────
describe('getRectanglePromptElement', () => {
  it('builds a rectangle prompt from event bounds', () => {
    const event = {
      layer: {
        _leaflet_id: 99,
        _bounds: {
          _northEast: { lat: 46.0, lng: 11.0 },
          _southWest: { lat: 44.0, lng: 9.0 },
        },
      },
    }
    const result = getRectanglePromptElement(event)
    expect(result.id).toBe(99)
    expect(result.type).toBe('rectangle')
    expect(result.data.ne.lat).toBe(46.0)
    expect(result.data.sw.lng).toBe(9.0)
  })
})

// ──────────────────────────────────────────────────────────
// getExtentCurrentViewMapBBox
// ──────────────────────────────────────────────────────────
describe('getExtentCurrentViewMapBBox', () => {
  /**
   * Mock LMap.getBounds() — returns an object with getNorthEast/getSouthWest methods.
   * This avoids needing a real Leaflet map with DOM container.
   */
  const makeMockMap = (ne: object, sw: object) => ({
    getBounds: () => ({
      getNorthEast: () => ne,
      getSouthWest: () => sw,
    }),
  })

  it('returns ne/sw from map bounds', () => {
    const ne = { lat: 46, lng: 11 }
    const sw = { lat: 44, lng: 9 }
    const map = makeMockMap(ne, sw)
    const result = getExtentCurrentViewMapBBox(map)
    expect(result).toEqual({ ne, sw })
  })
})

// ──────────────────────────────────────────────────────────
// updateZoomBboxMap
// ──────────────────────────────────────────────────────────
describe('updateZoomBboxMap', () => {
  /**
   * Side-effect function: updates Vue refs (currentZoomRef, currentMapBBoxRef).
   * We assert on the ref values after the call. The mock map provides
   * getZoom() and getBounds() — the two accessors the function uses.
   */

  it('updates currentZoomRef and currentMapBBoxRef from map state', () => {
    const ne = { lat: 46, lng: 11 }
    const sw = { lat: 44, lng: 9 }
    const mockMap = {
      getZoom: () => 13,
      getBounds: () => ({
        getNorthEast: () => ne,
        getSouthWest: () => sw,
      }),
    }

    updateZoomBboxMap(mockMap)

    expect(currentZoomRef.value).toBe(13)
    expect(currentMapBBoxRef.value).toEqual({ ne, sw })
  })
})

// ──────────────────────────────────────────────────────────
// getQueryParams
// ──────────────────────────────────────────────────────────
describe('getQueryParams', () => {
  /**
   * Reads from window.location.search (jsdom environment).
   * We use Object.defineProperty to override the read-only `search` property
   * because jsdom's window.location is not directly writable.
   */
  const originalSearch = window.location.search

  afterEach(() => {
    Object.defineProperty(window, 'location', {
      value: { ...window.location, search: originalSearch },
      writable: true,
    })
  })

  const setSearch = (search: string) => {
    Object.defineProperty(window, 'location', {
      value: { ...window.location, search },
      writable: true,
    })
  }

  it('parses source and other options from query string', () => {
    setSearch('?source=satellite&zoom=15&lat=45')
    const { source, options } = getQueryParams()
    expect(source).toBe('satellite')
    expect(options).toEqual({ zoom: '15', lat: '45' })
  })

  it('returns undefined source when not present in query', () => {
    setSearch('?zoom=10')
    const { source, options } = getQueryParams()
    expect(source).toBeUndefined()
    expect(options).toEqual({ zoom: '10' })
  })

  it('returns undefined source and empty options for empty query', () => {
    setSearch('')
    const { source, options } = getQueryParams()
    expect(source).toBeUndefined()
    expect(options).toEqual({})
  })

  it('handles source-only query string', () => {
    setSearch('?source=osm')
    const { source, options } = getQueryParams()
    expect(source).toBe('osm')
    expect(options).toEqual({})
  })
})

// ──────────────────────────────────────────────────────────
// getGeoJSONRequest
// ──────────────────────────────────────────────────────────
describe('getGeoJSONRequest', () => {
  /**
   * This function calls `fetch()`, parses nested JSON from the response,
   * and updates several Vue refs as side effects:
   * - responseMessageRef: set to waitingString before fetch, cleared on success
   * - durationRef, numberOfPolygonsRef, numberOfPredictedMasksRef: from parsed response
   *
   * We mock global.fetch and restore it after each test to avoid leaking state.
   * Console errors are suppressed for error-path tests to keep output clean.
   */

  const mockBody = {
    bbox: { ne: { lat: 46, lng: 11 }, sw: { lat: 44, lng: 9 } },
    prompt: [],
    zoom: 13,
    source_type: 'OpenStreetMap',
  }

  const validParsedOutput = {
    duration_run: 1.5,
    output: {
      geojson: '{"type":"FeatureCollection","features":[]}',
      n_predictions: 3,
      n_shapes_geojson: 2,
    },
  }

  /** Helper: create a mock Response for a 200 success case with nested JSON body. */
  const make200Response = (parsedOutput: object) => ({
    status: 200,
    json: () => Promise.resolve({ body: JSON.stringify(parsedOutput) }),
  })

  beforeEach(() => {
    responseMessageRef.value = '-'
    durationRef.value = 0
    numberOfPolygonsRef.value = 0
    numberOfPredictedMasksRef.value = 0
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sets responseMessageRef to waitingString before fetch resolves', async () => {
    /**
     * We capture the ref value at the moment fetch is called,
     * before any response processing happens.
     */
    let messageAtFetchTime = ''
    vi.spyOn(global, 'fetch').mockImplementation(() => {
      messageAtFetchTime = responseMessageRef.value
      return Promise.resolve(make200Response(validParsedOutput))
    })

    await getGeoJSONRequest(mockBody, '/infer_samgis')
    expect(messageAtFetchTime).toBe(waitingString)
  })

  it('returns parsed geojson and updates refs on 200 success', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(make200Response(validParsedOutput))

    const result = await getGeoJSONRequest(mockBody, '/infer_samgis')

    expect(result).toEqual({ type: 'FeatureCollection', features: [] })
    expect(durationRef.value).toBe(1.5)
    expect(numberOfPolygonsRef.value).toBe(2)
    expect(numberOfPredictedMasksRef.value).toBe(3)
    expect(responseMessageRef.value).toBe('')
  })

  it('sends POST with JSON content-type header', async () => {
    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue(make200Response(validParsedOutput))

    await getGeoJSONRequest(mockBody, '/infer_samgis')

    expect(fetchSpy).toHaveBeenCalledWith('/infer_samgis', {
      method: 'POST',
      body: JSON.stringify(mockBody),
      headers: { 'Content-type': 'application/json' },
    })
  })

  it('sets error message on non-200 status', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(global, 'fetch').mockResolvedValue({
      status: 500,
      text: () => Promise.resolve('Internal Server Error'),
    })

    await getGeoJSONRequest(mockBody, '/infer_samgis')

    expect(responseMessageRef.value).toBe('error message response: Internal Server Error...')
  })

  it('sets error status message when fetch response throws during processing', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    /**
     * Simulates a scenario where response.json() or response.text() throws
     * (e.g., network interruption mid-stream). The outer catch handles this.
     */
    vi.spyOn(global, 'fetch').mockResolvedValue({
      status: 200,
      json: () => { throw new Error('parse failure') },
      statusText: 'OK',
    })

    await getGeoJSONRequest(mockBody, '/infer_samgis')

    expect(responseMessageRef.value).toBe('error status response: OK...')
  })

  it('handles missing statusText gracefully', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(global, 'fetch').mockResolvedValue({
      status: 200,
      json: () => { throw new Error('fail') },
      statusText: '',
    })

    await getGeoJSONRequest(mockBody, '/infer_samgis')

    /** Falls back to a generic message when statusText is empty/falsy. */
    expect(responseMessageRef.value).toBe('error status response: no response or uncaught exception!...')
  })

  it('handles malformed output.body JSON gracefully', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(global, 'fetch').mockResolvedValue({
      status: 200,
      json: () => Promise.resolve({ body: 'not-valid-json' }),
    })

    /**
     * When JSON.parse(output.body) fails, the inner catch returns
     * the stringified error — the function doesn't throw.
     */
    const result = await getGeoJSONRequest(mockBody, '/infer_samgis')
    expect(typeof result).toBe('string')
    expect(result).toContain('SyntaxError')
  })
})

// ──────────────────────────────────────────────────────────
// getPopupContentPoint
// ──────────────────────────────────────────────────────────
describe('getPopupContentPoint', () => {
  /**
   * Builds an HTMLDivElement popup for a point marker.
   * The event mock needs `layer._latlng` (for coordinates)
   * and `layer._leaflet_id` (displayed in the popup text).
   * jsdom provides full DOM APIs so we can assert on the returned element.
   */

  const makePointEvent = (lat: number, lng: number, leafletId: number) => ({
    layer: { _latlng: { lat, lng }, _leaflet_id: leafletId },
  })

  it('returns an HTMLDivElement', () => {
    const event = makePointEvent(45.5, 9.2, 42)
    const result = getPopupContentPoint(event, 1)
    expect(result).toBeInstanceOf(HTMLDivElement)
  })

  it('outer div has class "leaflet-popup-content-inner"', () => {
    const event = makePointEvent(45.5, 9.2, 42)
    const result = getPopupContentPoint(event, 1)
    expect(result.className).toBe('leaflet-popup-content-inner')
  })

  it('contains lat value from event', () => {
    const event = makePointEvent(45.5, 9.2, 42)
    const result = getPopupContentPoint(event, 1)
    expect(result.textContent).toContain('lat:45.5')
  })

  it('contains lng value from event', () => {
    const event = makePointEvent(45.5, 9.2, 42)
    const result = getPopupContentPoint(event, 1)
    expect(result.textContent).toContain('lng:9.2')
  })

  it('contains label value', () => {
    const event = makePointEvent(45.5, 9.2, 42)
    const result = getPopupContentPoint(event, 1)
    expect(result.textContent).toContain('label:1')
  })

  it('contains leaflet id', () => {
    const event = makePointEvent(45.5, 9.2, 42)
    const result = getPopupContentPoint(event, 1)
    expect(result.textContent).toContain('id:42')
  })

  it('works with label 0 (exclude) — falsy but valid', () => {
    const event = makePointEvent(44.0, 8.0, 7)
    const result = getPopupContentPoint(event, 0)
    expect(result.textContent).toContain('label:0')
    expect(result.textContent).toContain('id:7')
  })

  it('preserves decimal precision in coordinates', () => {
    const event = makePointEvent(46.123456789, 9.987654321, 99)
    const result = getPopupContentPoint(event, 1)
    expect(result.textContent).toContain('lat:46.123456789')
    expect(result.textContent).toContain('lng:9.987654321')
  })
})
