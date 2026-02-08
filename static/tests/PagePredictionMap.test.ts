import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'

/**
 * Partial mocks for Leaflet, leaflet-providers, geoman, and driver.js.
 * We mock just enough for onMounted/onUpdated to complete without errors,
 * so we can test template rendering via shallowMount.
 *
 * The mockMapInstance is defined inside the factory to avoid hoisting issues:
 * vi.mock is hoisted above imports, so top-level references to vi.fn() would
 * be undefined at factory execution time.
 */

const mockLayerControl = { addOverlay: vi.fn() }

const mockMapInstance = {
  fitBounds: vi.fn(),
  attributionControl: { setPrefix: vi.fn() },
  on: vi.fn(),
  options: { maxBoundsViscosity: 0 },
  pm: {
    addControls: vi.fn(),
    setPathOptions: vi.fn(),
    Toolbar: {
      copyDrawControl: vi.fn(() => ({
        drawInstance: { setOptions: vi.fn() },
      })),
    },
  },
  getZoom: vi.fn(() => 10),
  getBounds: vi.fn(() => ({
    getNorthEast: () => ({ lat: 46, lng: 11 }),
    getSouthWest: () => ({ lat: 44, lng: 9 }),
  })),
  setMaxZoom: vi.fn(),
  setMinZoom: vi.fn(),
  setMaxBounds: vi.fn(),
  addLayer: vi.fn(),
}

vi.mock('leaflet', async () => {
  const actual = await vi.importActual('leaflet')
  return {
    ...actual,
    /** LeafletMap('map', {...}) — the `map` factory function */
    map: vi.fn(() => mockMapInstance),
    tileLayer: {
      ...actual.tileLayer,
      provider: vi.fn(() => ({ _url: 'mock-url' })),
    },
    /** `new LTileLayer(url, opts)` — must be a class/constructor */
    TileLayer: class MockTileLayer {
      _url: string
      constructor(url: string) { this._url = url }
    },
    control: {
      scale: vi.fn(() => ({ addTo: vi.fn() })),
      layers: vi.fn(() => ({ addTo: vi.fn(() => mockLayerControl) })),
    },
    Control: {
      ...actual.Control,
      Layers: class MockLayers {},
    },
    icon: vi.fn(() => ({})),
  }
})

vi.mock('leaflet-providers', () => ({}))
vi.mock('@geoman-io/leaflet-geoman-free', () => ({}))
vi.mock('driver.js', () => ({
  driver: vi.fn(() => ({ drive: vi.fn() })),
}))

import PagePredictionMap from '@/components/PagePredictionMap.vue'
import {
  mapNavigationLocked,
  promptsArrayRef,
  responseMessageRef,
} from '@/components/constants'

const defaultProps = {
  mapBounds: [
    { lat: 46.23, lng: 9.47 },
    { lat: 46.13, lng: 9.30 },
  ],
  mapName: 'test-map',
  description: 'Test map description',
}

describe('PagePredictionMap — template', () => {
  beforeEach(() => {
    mapNavigationLocked.value = false
    promptsArrayRef.value = []
    responseMessageRef.value = '-'
    vi.clearAllMocks()
  })

  it('renders container with id "id-prediction-map-container"', () => {
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    expect(wrapper.find('#id-prediction-map-container').exists()).toBe(true)
  })

  it('renders description text', () => {
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    expect(wrapper.find('p').text()).toBe('Test map description')
  })

  it('renders map div with id "map"', () => {
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    expect(wrapper.find('#map').exists()).toBe(true)
  })

  it('shows "map navigation unlocked" label by default', () => {
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    const label = wrapper.find('label')
    expect(label.text()).toBe('map navigation unlocked')
  })

  it('shows "locked map navigation!" label when mapNavigationLocked is true', async () => {
    mapNavigationLocked.value = true
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    await wrapper.vm.$nextTick()
    const label = wrapper.find('label')
    expect(label.text()).toBe('locked map navigation!')
  })

  it('renders Map Info heading', () => {
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    const h1s = wrapper.findAll('h1')
    const mapInfoH1 = h1s.find(h => h.text() === 'Map Info')
    expect(mapInfoH1).toBeDefined()
  })

  it('renders ML request prompt heading', () => {
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    expect(wrapper.find('#id-ml-request-prompt').text()).toBe('ML request prompt')
  })

  it('hides points table when no point prompts', () => {
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    const tables = wrapper.findAllComponents({ name: 'TableGenericComponent' })
    expect(tables).toHaveLength(0)
  })

  it('hides rectangles table when no rectangle prompts', () => {
    promptsArrayRef.value = [
      { id: 1, type: 'point', data: { lat: 45, lng: 9 }, label: 1 },
    ]
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    const tables = wrapper.findAllComponents({ name: 'TableGenericComponent' })
    expect(tables).toHaveLength(1)
  })

  it('shows responseMessage in h2 when truthy and not waitingString', () => {
    responseMessageRef.value = 'error: something failed'
    const wrapper = shallowMount(PagePredictionMap, { props: defaultProps })
    const h2 = wrapper.find('h2')
    expect(h2.text()).toBe('error: something failed')
  })
})
