import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TableGenericComponent from '@/components/TableGenericComponent.vue'

const pointRows = [
  { id: 1, data: '45.5, 9.2', label: 1 },
  { id: 2, data: '44.0, 8.0', label: 0 },
]

const rectRows = [
  { id: 10, data_ne: '46.0, 11.0', data_sw: '44.0, 9.0' },
  { id: 20, data_ne: '47.0, 12.0', data_sw: '45.0, 10.0' },
]

const defaultProps = {
  header: ['id', 'data', 'label'],
  rows: pointRows,
  title: 'Points',
  rowKey: 'id',
}

describe('TableGenericComponent', () => {
  it('renders caption with title prop', () => {
    const wrapper = mount(TableGenericComponent, { props: defaultProps })
    expect(wrapper.find('caption').text()).toBe('Points')
  })

  it('renders header cells from header array', () => {
    const wrapper = mount(TableGenericComponent, { props: defaultProps })
    const thElements = wrapper.findAll('th')
    expect(thElements).toHaveLength(3)
    expect(thElements.map(th => th.text())).toEqual(['id', 'data', 'label'])
  })

  it('renders one tbody per row', () => {
    const wrapper = mount(TableGenericComponent, { props: defaultProps })
    expect(wrapper.findAll('tbody')).toHaveLength(2)
  })

  it('renders cell values from row objects', () => {
    const wrapper = mount(TableGenericComponent, { props: defaultProps })
    const tdElements = wrapper.findAll('td')
    expect(tdElements).toHaveLength(6) // 2 rows x 3 cells
    expect(tdElements[0].text()).toBe('1')
    expect(tdElements[1].text()).toBe('45.5, 9.2')
    expect(tdElements[2].text()).toBe('1')
    expect(tdElements[3].text()).toBe('2')
    expect(tdElements[4].text()).toBe('44.0, 8.0')
    expect(tdElements[5].text()).toBe('0')
  })

  it('renders empty table when rows is empty', () => {
    const wrapper = mount(TableGenericComponent, {
      props: { ...defaultProps, rows: [] },
    })
    expect(wrapper.findAll('tbody')).toHaveLength(0)
    expect(wrapper.findAll('th')).toHaveLength(3) // header still rendered
  })

  it('renders rectangle rows with different object shape', () => {
    const wrapper = mount(TableGenericComponent, {
      props: {
        header: ['id', 'data_ne', 'data_sw'],
        rows: rectRows,
        title: 'Rectangles',
        rowKey: 'id',
      },
    })
    expect(wrapper.findAll('tbody')).toHaveLength(2)
    const tdElements = wrapper.findAll('td')
    expect(tdElements).toHaveLength(6)
    expect(tdElements[0].text()).toBe('10')
    expect(tdElements[1].text()).toBe('46.0, 11.0')
  })

  it('renders single row correctly', () => {
    const wrapper = mount(TableGenericComponent, {
      props: { ...defaultProps, rows: [pointRows[0]] },
    })
    expect(wrapper.findAll('tbody')).toHaveLength(1)
    expect(wrapper.findAll('td')).toHaveLength(3)
  })
})
