import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PageFooterHyperlink from '@/components/PageFooterHyperlink.vue'

describe('PageFooterHyperlink', () => {
  it('renders href from path prop', () => {
    const wrapper = mount(PageFooterHyperlink, {
      props: { path: 'https://example.com' },
      slots: { default: 'link text' },
    })
    expect(wrapper.find('a').attributes('href')).toBe('https://example.com')
  })

  it('renders slot content as link text', () => {
    const wrapper = mount(PageFooterHyperlink, {
      props: { path: '/' },
      slots: { default: 'SamGIS' },
    })
    expect(wrapper.find('a').text()).toBe('SamGIS')
  })

  it('opens in new tab with target="_blank"', () => {
    const wrapper = mount(PageFooterHyperlink, {
      props: { path: '/' },
      slots: { default: 'link' },
    })
    expect(wrapper.find('a').attributes('target')).toBe('_blank')
  })

  it('has rel="noopener noreferrer" for tab-nabbing protection', () => {
    const wrapper = mount(PageFooterHyperlink, {
      props: { path: '/' },
      slots: { default: 'link' },
    })
    expect(wrapper.find('a').attributes('rel')).toBe('noopener noreferrer')
  })

  it('renders HTML slot content', () => {
    const wrapper = mount(PageFooterHyperlink, {
      props: { path: '/' },
      slots: { default: '<strong>bold link</strong>' },
    })
    expect(wrapper.find('a strong').text()).toBe('bold link')
  })
})
