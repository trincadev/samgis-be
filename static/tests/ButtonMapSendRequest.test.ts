import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ButtonMapSendRequest from '@/components/buttons/ButtonMapSendRequest.vue'

/**
 * The `map` prop expects a Leaflet LMap instance.
 * We pass a plain object since the component only forwards it to sendMLRequest —
 * no Leaflet methods are called directly by this component.
 */
const mockMap = {} as any

const samplePrompt = { id: 1, type: 'point', data: { lat: 45, lng: 9 }, label: 1 }

const baseProps = {
  class: 'test-class',
  currentBaseMapName: 'OpenStreetMap',
  promptsArray: [samplePrompt],
  responseMessage: '-',
  map: mockMap,
  sendMLRequest: vi.fn(),
  waitingString: 'waiting...',
}

describe('ButtonMapSendRequest', () => {
  // ── State 1: empty prompt ──────────────────────────────
  it('shows disabled button with empty prompt text when promptsArray is empty', () => {
    const wrapper = mount(ButtonMapSendRequest, {
      props: { ...baseProps, promptsArray: [] },
    })
    const button = wrapper.find('button')
    expect(button.text()).toContain('Empty prompt (disabled)')
    expect(button.attributes('disabled')).toBeDefined()
  })

  // ── State 2: waiting ───────────────────────────────────
  it('shows disabled button with waitingString when responseMessage equals waitingString', () => {
    const wrapper = mount(ButtonMapSendRequest, {
      props: { ...baseProps, responseMessage: 'waiting...' },
    })
    const button = wrapper.find('button')
    expect(button.text()).toBe('waiting...')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('waiting state takes priority over empty prompt when both conditions true', () => {
    const wrapper = mount(ButtonMapSendRequest, {
      props: { ...baseProps, promptsArray: [], responseMessage: 'waiting...' },
    })
    expect(wrapper.find('button').text()).toBe('waiting...')
  })

  // ── State 3: ready (default) ───────────────────────────
  it('shows send ML request text when prompts present and responseMessage is "-"', () => {
    const wrapper = mount(ButtonMapSendRequest, { props: baseProps })
    expect(wrapper.find('button').text()).toContain('send ML request')
  })

  it('shows send ML request text when prompts present and responseMessage is empty', () => {
    const wrapper = mount(ButtonMapSendRequest, {
      props: { ...baseProps, responseMessage: '' },
    })
    expect(wrapper.find('button').text()).toContain('send ML request')
  })

  it('enabled button is not disabled', () => {
    const wrapper = mount(ButtonMapSendRequest, { props: baseProps })
    expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
  })

  // ── State 4: has response message ──────────────────────
  it('shows responseMessage when truthy and not "-"', () => {
    const wrapper = mount(ButtonMapSendRequest, {
      props: { ...baseProps, responseMessage: 'error: timeout' },
    })
    expect(wrapper.find('button').text()).toBe('error: timeout')
  })

  // ── Click behavior ─────────────────────────────────────
  it('calls sendMLRequest with map, promptsArray, currentBaseMapName on click', async () => {
    const sendFn = vi.fn()
    const wrapper = mount(ButtonMapSendRequest, {
      props: { ...baseProps, sendMLRequest: sendFn },
    })
    await wrapper.find('button').trigger('click')
    expect(sendFn).toHaveBeenCalledOnce()
    expect(sendFn).toHaveBeenCalledWith(mockMap, [samplePrompt], 'OpenStreetMap')
  })
})
