import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatsGrid from '@/components/StatsGrid.vue'

const defaultProps = {
  statsArray: [
    { statName: 'current Zoom', statValue: '13' },
    { statName: 'current map name/type', statValue: 'OpenStreetMap' },
    { statName: 'prompt: points/rectangles number', statValue: '2' },
  ],
}

describe('StatsGrid', () => {
  it('renders one dl per stat item', () => {
    const wrapper = mount(StatsGrid, { props: defaultProps })
    expect(wrapper.findAll('dl')).toHaveLength(3)
  })

  it('renders stat names in dt elements', () => {
    const wrapper = mount(StatsGrid, { props: defaultProps })
    const dtElements = wrapper.findAll('dt')
    expect(dtElements.map(dt => dt.text())).toEqual([
      'current Zoom',
      'current map name/type',
      'prompt: points/rectangles number',
    ])
  })

  it('renders stat values in dd elements', () => {
    const wrapper = mount(StatsGrid, { props: defaultProps })
    const ddElements = wrapper.findAll('dd')
    expect(ddElements.map(dd => dd.text())).toEqual(['13', 'OpenStreetMap', '2'])
  })

  it('renders empty when statsArray is empty', () => {
    const wrapper = mount(StatsGrid, { props: { statsArray: [] } })
    expect(wrapper.findAll('dl')).toHaveLength(0)
  })

  it('renders single item', () => {
    const wrapper = mount(StatsGrid, {
      props: { statsArray: [{ statName: 'zoom', statValue: '5' }] },
    })
    expect(wrapper.findAll('dl')).toHaveLength(1)
    expect(wrapper.find('dt').text()).toBe('zoom')
    expect(wrapper.find('dd').text()).toBe('5')
  })
})
