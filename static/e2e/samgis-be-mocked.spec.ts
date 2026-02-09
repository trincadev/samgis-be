import { test, expect } from './fixtures';


test('UI updates after mocked /infer_samgis response', async ({ mockedPage }) => {
    await mockedPage.goto('/');

    // Dismiss the driver.js tour by clicking on driver.js dialog, then pressing ESCAPE on the keyboard
    await mockedPage.getByRole('dialog', { name: 'SamGIS' }).click();
    await mockedPage.locator('body').press('Escape');

    // Verify send button is initially disabled (no prompts)
    const disabledButton = mockedPage.locator('#id-button-submit');
    await expect(disabledButton).toContainText('Empty prompt (disabled)');

    // selection (positive) marker
    await mockedPage.getByRole('button').filter({ hasText: /^$/ }).nth(4).click();
    await expect(mockedPage.getByRole('button', { name: 'Marker' })).toBeVisible();
    await mockedPage.getByText('Click to place marker+−').click();

    // Then after response, verify stats appear
    const mapInfo = mockedPage.locator('#id-map-info');
    await expect(mapInfo).toMatchAriaSnapshot({ name: 'mapInfoBeforeRequest.0.aria.yaml'})

    /**
     * Inject a fake point prompt into the Vue reactive state.
     * Vite's dev server exposes source modules via ESM — we can import
     * the constants module directly in the browser context using its
     * dev server path (not a Node.js filesystem path).
     */
    await mockedPage.evaluate(async () => {
        const mod = await import('/src/components/constants.ts');
        mod.promptsArrayRef.value = [
            { id: 1108, type: 'point', data: { lat: 46.16, lng: 9.39 }, label: 1 },
        ];
    });

    // Wait for Vue reactivity to update the button
    const sendButton = mockedPage.locator('#id-button-submit');
    await expect(sendButton).toContainText('send ML request', { timeout: 500 });

    // Click the send button — triggers fetch to /infer_samgis (mocked)
    await sendButton.click();

    // Verify UI shows "waiting..." while request is in flight

    // After successful response: duration, polygons, predicted masks stats should appear
    await expect(mapInfo).toMatchAriaSnapshot({ name: 'mapInfoAfterRequest.0.aria.yaml'})

    // Map navigation should be locked after request
    const checkbox = mockedPage.locator('#checkboxMapNavigationLocked');
    await expect(checkbox).toBeChecked();

    // The locked label should show
    await expect(mockedPage.locator('label').filter({ hasText: 'locked map navigation!' })).toBeVisible();

    await mockedPage.close();
});
