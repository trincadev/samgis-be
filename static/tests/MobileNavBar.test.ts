import { describe, it, expect } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import MobileNavBar from '@/components/NavBar/MobileNavBar.vue'

describe('MobileNavBar', () => {
  it('renders a container div with bg-gray-200 class', () => {
    const wrapper = shallowMount(MobileNavBar)
    expect(wrapper.find('div.bg-gray-200').exists()).toBe(true)
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
    expect(tabs[2].props('href')).toBe('https://docs.trinca.tornidor.com/')
  })

  it('passes correct descriptions to TabComponents', () => {
    const wrapper = shallowMount(MobileNavBar)
    const tabs = wrapper.findAllComponents({ name: 'TabComponent' })
    expect(tabs[0].props('description')).toBe('About SamGIS')
    expect(tabs[1].props('description')).toBe('My blog')
    expect(tabs[2].props('description')).toBe('SamGIS docs')
  })
})
