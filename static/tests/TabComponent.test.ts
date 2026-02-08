import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TabComponent from '@/components/NavBar/TabComponent.vue'

describe('TabComponent', () => {
  const defaultProps = {
    href: 'https://example.com',
    description: 'Example Link',
  }

  it('renders href from prop', () => {
    const wrapper = mount(TabComponent, { props: defaultProps })
    expect(wrapper.find('a').attributes('href')).toBe('https://example.com')
  })

  it('renders description as link text', () => {
    const wrapper = mount(TabComponent, { props: defaultProps })
    expect(wrapper.find('a').text()).toBe('Example Link')
  })

  it('wraps link in h2', () => {
    const wrapper = mount(TabComponent, { props: defaultProps })
    expect(wrapper.find('h2 a').exists()).toBe(true)
  })
})
