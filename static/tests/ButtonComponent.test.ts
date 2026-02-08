import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ButtonComponent from '@/components/buttons/ButtonComponent.vue'

describe('ButtonComponent', () => {
  it('renders slot content', () => {
    const wrapper = mount(ButtonComponent, {
      props: { click: () => {} },
      slots: { default: 'Click me' },
    })
    expect(wrapper.find('button').text()).toBe('Click me')
  })

  it('calls click prop on click', async () => {
    const clickFn = vi.fn()
    const wrapper = mount(ButtonComponent, {
      props: { click: clickFn },
      slots: { default: 'Click me' },
    })
    await wrapper.find('button').trigger('click')
    expect(clickFn).toHaveBeenCalledOnce()
  })

  it('renders HTML slot content', () => {
    const wrapper = mount(ButtonComponent, {
      props: { click: () => {} },
      slots: { default: '<span>icon</span> Save' },
    })
    expect(wrapper.find('button span').text()).toBe('icon')
  })
})
