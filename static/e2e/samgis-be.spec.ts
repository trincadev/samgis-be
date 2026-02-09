import { test, expect } from '@playwright/test';


test('test the driver.js tour on the localhost SamGIS-be page', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('dialog', { name: 'SamGIS' })).toBeVisible();
    await expect(page.locator('#driver-popover-description')).toContainText('A quick tour about SamGIS functionality');
    await expect(page.getByRole('contentinfo')).toContainText('1 of 9');
    await page.getByRole('button', { name: 'Next →' }).click();
    await expect(page.getByRole('dialog', { name: 'Webmap for ML prompt' })).toBeVisible();

    await page.getByRole('button', { name: 'Next →' }).click();
    await expect(page.getByRole('dialog', { name: '"Include" point prompt' })).toBeVisible();

    await page.getByRole('button', { name: 'Next →' }).click();
    await expect(page.getByRole('dialog', { name: '"Exclude" point prompt' })).toBeVisible();

    await page.getByRole('button', { name: 'Next →' }).click();
    await expect(page.getByRole('dialog', { name: '"Include" rectangle prompt' })).toBeVisible();

    await page.getByRole('button', { name: 'Next →' }).click();
    await expect(page.getByRole('dialog', { name: 'ML submit button' })).toBeVisible();

    await page.getByRole('button', { name: 'Next →' }).click();
    await expect(page.getByRole('dialog', { name: 'Map provider selector' })).toBeVisible();

    await page.getByRole('button', { name: 'Next →' }).click();
    await expect(page.getByRole('dialog', { name: 'map info' })).toBeVisible();

    await page.getByRole('button', { name: 'Next →' }).click();
    await expect(page.locator('#driver-popover-description')).toContainText(
      'Empty at beginning, this table will contain the machine learning prompt (points and rectangles) section'
    );
    await page.getByRole('button', { name: 'Done' }).click();

    const navigationMapLock = page.getByRole('checkbox', { name: 'map navigation unlocked' })
    await expect(navigationMapLock).toBeVisible()
    await expect(navigationMapLock).not.toBeChecked()

    const mapLocator = page.locator("#map")
    await expect(mapLocator).toBeVisible()
    await expect(mapLocator).toMatchAriaSnapshot({ name: 'mapLocatorTestDriverJS.aria.yaml'})

    const sendButton = page.getByRole('button', { name: 'Empty prompt (disabled)' })
    await expect(sendButton).toBeVisible()
    await expect(sendButton).toBeDisabled()
    await page.close();
});
