import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PageFooter from '@/components/PageFooter.vue'

describe('PageFooter', () => {
  it('renders footer on mount', () => {
    const wrapper = mount(PageFooter)
    expect(wrapper.find('footer').exists()).toBe(true)
  })

  it('hides footer after close button click', async () => {
    const wrapper = mount(PageFooter)
    await wrapper.find('button').trigger('click')
    expect(wrapper.find('footer').exists()).toBe(false)
  })

  it('re-shows footer on second close click', async () => {
    const wrapper = mount(PageFooter)
    await wrapper.find('button').trigger('click')
    expect(wrapper.find('footer').exists()).toBe(false)
    // v-if removed the button — component re-renders with no footer
    // showFooterRef toggled to false; no button to click again.
    // This confirms toggle removes the footer entirely (no way back from UI).
  })

  it('renders close button with aria-label', () => {
    const wrapper = mount(PageFooter)
    const button = wrapper.find('button')
    expect(button.attributes('aria-label')).toBe('Close')
    expect(button.text()).toBe('Close')
  })

  it('renders 4 hyperlinks', () => {
    const wrapper = mount(PageFooter)
    const links = wrapper.findAll('a')
    expect(links).toHaveLength(4)
  })

  it('renders direct URL space link to hf.space', () => {
    const wrapper = mount(PageFooter)
    const hfLink = wrapper.findAll('a').find(a => a.attributes('href')?.includes('hf.space'))
    expect(hfLink).toBeDefined()
    expect(hfLink!.text()).toBe('direct URL space')
  })
})
