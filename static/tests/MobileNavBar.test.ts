import { describe, it, expect } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import MobileNavBar from '@/components/NavBar/MobileNavBar.vue'

describe('MobileNavBar', () => {
  it('renders a container nav with bg-gray-200 class', () => {
    const wrapper = shallowMount(MobileNavBar)
    const nav = wrapper.find('nav.bg-gray-200')
    expect(nav.exists()).toBe(true)
    expect(nav.attributes('data-testid')).toBe('mobile-navbar')
    expect(nav.attributes('aria-label')).toBe('Mobile navigation')
  })

  it('renders exactly three TabComponent instances', () => {
    const wrapper = shallowMount(MobileNavBar)
    const tabs = wrapper.findAllComponents({ name: 'TabComponent' })
    expect(tabs).toHaveLength(3)
  })

  it('passes correct hrefs to TabComponents', () => {
    const wrapper = shallowMount(MobileNavBar)
    const tabs = wrapper.findAllComponents({ name: 'TabComponent' })
    expect(tabs[0].props('href')).toBe(
      'https://trinca.tornidor.com/projects/samgis-segment-anything-applied-to-GIS'
    )
    expect(tabs[1].props('href')).toBe('https://trinca.tornidor.com/')
    expect(tabs[2].props('href')).toBe('https://docs.ml-trinca.tornidor.com/')
  })

  it('passes correct descriptions to TabComponents', () => {
    const wrapper = shallowMount(MobileNavBar)
    const tabs = wrapper.findAllComponents({ name: 'TabComponent' })
    expect(tabs[0].props('description')).toBe('About SamGIS')
    expect(tabs[1].props('description')).toBe('My blog')
    expect(tabs[2].props('description')).toBe('SamGIS docs')
  })
})
