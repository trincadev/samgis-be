import { describe, it, expect } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import NavBar from '@/components/NavBar/NavBar.vue'

describe('NavBar', () => {
  it('renders a fixed-position container nav', () => {
    const wrapper = shallowMount(NavBar)
    const nav = wrapper.find('nav.fixed')
    expect(nav.exists()).toBe(true)
    expect(nav.classes()).toContain('top-2')
    expect(nav.classes()).toContain('right-5')
    expect(nav.attributes('data-testid')).toBe('navbar')
    expect(nav.attributes('aria-label')).toBe('Main navigation')
  })

  it('renders exactly three TabComponent instances', () => {
    const wrapper = shallowMount(NavBar)
    const tabs = wrapper.findAllComponents({ name: 'TabComponent' })
    expect(tabs).toHaveLength(3)
  })

  it('passes correct hrefs to TabComponents', () => {
    const wrapper = shallowMount(NavBar)
    const tabs = wrapper.findAllComponents({ name: 'TabComponent' })
    expect(tabs[0].props('href')).toBe(
      'https://trinca.tornidor.com/projects/samgis-segment-anything-applied-to-GIS'
    )
    expect(tabs[1].props('href')).toBe('https://trinca.tornidor.com/')
    expect(tabs[2].props('href')).toBe('https://docs.ml-trinca.tornidor.com/')
  })

  it('passes correct descriptions to TabComponents', () => {
    const wrapper = shallowMount(NavBar)
    const tabs = wrapper.findAllComponents({ name: 'TabComponent' })
    expect(tabs[0].props('description')).toBe('About SamGIS')
    expect(tabs[1].props('description')).toBe('My blog')
    expect(tabs[2].props('description')).toBe('SamGIS docs')
  })
})
