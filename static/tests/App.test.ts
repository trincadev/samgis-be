import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import App from '@/App.vue'
import PredictionMap from '@/components/PagePredictionMap.vue'

/**
 * shallowMount(App) stubs PageLayout, which swallows its slot content —
 * PredictionMap never renders. We provide a pass-through stub for PageLayout
 * that renders the slot, while PredictionMap stays stubbed (via shallowMount default).
 */
const stubs = {
  PageLayout: {
    template: '<div class="page-layout-stub"><slot /></div>',
    props: ['pageTitle'],
  },
}

describe('App', () => {
  beforeEach(() => {
    vi.unstubAllEnvs()
  })

  it('renders PageLayout with correct pageTitle', () => {
    const wrapper = shallowMount(App, { global: { stubs } })
    const layout = wrapper.findComponent(stubs.PageLayout)
    expect(layout.exists()).toBe(true)
    expect(layout.props('pageTitle')).toBe('SamGIS - Inference map page')
  })

  it('renders PredictionMap component', () => {
    const wrapper = shallowMount(App, { global: { stubs } })
    const map = wrapper.findComponent(PredictionMap)
    expect(map.exists()).toBe(true)
  })

  it('passes default description when env var not set', () => {
    const wrapper = shallowMount(App, { global: { stubs } })
    const map = wrapper.findComponent(PredictionMap)
    expect(map.props('description')).toBe(
      'This page displays predictions made with a machine learning model'
    )
  })

  it('passes env description when VITE__MAP_DESCRIPTION is set', async () => {
    vi.stubEnv('VITE__MAP_DESCRIPTION', 'Custom map description')
    const wrapper = shallowMount(App, { global: { stubs } })
    await wrapper.vm.$nextTick()
    const map = wrapper.findComponent(PredictionMap)
    expect(map.props('description')).toBe('Custom map description')
  })

  it('passes mapName "prediction-map" to PredictionMap', () => {
    const wrapper = shallowMount(App, { global: { stubs } })
    const map = wrapper.findComponent(PredictionMap)
    expect(map.props('mapName')).toBe('prediction-map')
  })

  it('passes hardcoded mapBounds to PredictionMap', () => {
    const wrapper = shallowMount(App, { global: { stubs } })
    const map = wrapper.findComponent(PredictionMap)
    const bounds = map.props('mapBounds')
    expect(bounds).toHaveLength(2)
    expect(bounds[0]).toEqual({ lat: 46.235421781941776, lng: 9.47699401855469 })
    expect(bounds[1]).toEqual({ lat: 46.1351347810282, lng: 9.30121276855469 })
  })
})
