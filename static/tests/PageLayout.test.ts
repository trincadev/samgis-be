import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PageLayout from '@/components/PageLayout.vue'

describe('PageLayout', () => {
  it('renders pageTitle in header', () => {
    const wrapper = mount(PageLayout, {
      props: { pageTitle: 'Test Page Title' },
      slots: { default: '<p>content</p>' },
    })
    expect(wrapper.find('header h2').text()).toBe('Test Page Title')
  })

  it('renders default slot content', () => {
    const wrapper = mount(PageLayout, {
      props: { pageTitle: 'Title' },
      slots: { default: '<p id="slot-content">hello</p>' },
    })
    expect(wrapper.find('#slot-content').text()).toBe('hello')
  })

  it('renders NavBar component', () => {
    const wrapper = mount(PageLayout, {
      props: { pageTitle: 'Title' },
      slots: { default: 'content' },
    })
    // NavBar and MobileNavBar both render TabComponent links
    // The full mount renders all children — check for at least one nav link
    const links = wrapper.findAll('a')
    expect(links.length).toBeGreaterThan(0)
  })

  it('renders Footer component', () => {
    const wrapper = mount(PageLayout, {
      props: { pageTitle: 'Title' },
      slots: { default: 'content' },
    })
    expect(wrapper.find('footer').exists()).toBe(true)
  })

  it('renders main content area', () => {
    const wrapper = mount(PageLayout, {
      props: { pageTitle: 'Title' },
      slots: { default: 'content' },
    })
    expect(wrapper.find('#content').exists()).toBe(true)
  })
})
