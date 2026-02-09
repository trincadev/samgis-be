import { test as base } from '@playwright/test'
import { readFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

/**
 * Custom fixture that intercepts the /infer_samgis API call
 * and returns the mocked response from colico-mocked-reponse.json.
 *
 * Usage in tests:
 *   import { test, expect } from './fixtures'
 *   test('my test', async ({ mockedPage }) => { ... })
 *
 * The `mockedPage` fixture:
 * - Intercepts POST /infer_samgis with the real Colico response
 * - Also intercepts /health with a 200 OK
 * - Navigates to the app root
 * - Dismisses the driver.js tour (clicks through all steps)
 */

const mockedResponsePath = resolve(__dirname, 'colico-mocked-reponse.json')
const mockedResponseBody = readFileSync(mockedResponsePath, 'utf-8')

export const test = base.extend<{ mockedPage: ReturnType<typeof base['page']> }>({
  mockedPage: async ({ page }, use) => {
    // Intercept the ML inference endpoint
    await page.route('**/infer_samgis', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: mockedResponseBody,
      })
    })

    // Intercept health check
    await page.route('**/health', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'ok' }),
      })
    })

    await use(page)
  },
})

export { expect } from '@playwright/test'
