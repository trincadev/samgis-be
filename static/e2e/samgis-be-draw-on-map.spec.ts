import { test, expect } from '@playwright/test';


test('test - after placing include/exclude markers on map their coordinate positions appear on the Point table', async ({ page }) => {
    await page.goto('/');
    
    // Dismiss the driver.js tour by clicking on driver.js dialog, then pressing ESCAPE on the keyboard
    await page.getByRole('dialog', { name: 'SamGIS' }).click();
    await page.locator('body').press('Escape');

    const tableMapMarkersPositions = page.getByRole('table', { name: 'Table with the position for the map markers' })
    const tableMapRectanglesPositions = page.getByRole('table', { name: 'Table with the position for the map rectangles' })

    // exclude marker – negative
    await page.getByRole('button').filter({ hasText: /^$/ }).nth(4).click();
    await expect(page.getByRole('button', { name: 'Marker' })).toBeVisible();

    await page.getByText('Click to place marker+−').click();
    await expect(tableMapMarkersPositions).toBeVisible();
    await expect(tableMapRectanglesPositions).not.toBeVisible();
    await expect(tableMapMarkersPositions).toMatchAriaSnapshot({ name: 'tableMapMarkersPositionsNegative.0.aria.yaml'})

    // cancel the existing marker
    await page.getByRole('button').filter({ hasText: /^$/ }).nth(3).click();
    await expect(page.getByRole('button', { name: 'Finish' })).toBeVisible();

    await page.getByRole('button', { name: 'Marker' }).click();
    await expect(tableMapMarkersPositions).not.toBeVisible();
    await expect(tableMapRectanglesPositions).not.toBeVisible();

    // include marker - positive
    await page.getByRole('button').filter({ hasText: /^$/ }).nth(3).click();
    await expect(page.getByRole('button', { name: 'Marker' })).toBeVisible();

    await page.getByText('Click to place marker+−').click();
    await expect(tableMapMarkersPositions).toBeVisible();
    await expect(tableMapRectanglesPositions).not.toBeVisible();
    await expect(tableMapMarkersPositions).toMatchAriaSnapshot({ name: 'tableMapMarkersPositionsPositive.0.aria.yaml'})

    // cancel the existing marker
    await page.getByRole('button').filter({ hasText: /^$/ }).nth(3).click();
    await expect(page.getByRole('button', { name: 'Finish' })).toBeVisible();

    await page.getByRole('button', { name: 'Marker' }).click();
    await expect(tableMapMarkersPositions).not.toBeVisible();
    await expect(tableMapRectanglesPositions).not.toBeVisible();

    // deselect the "eraser" tool
    await page.getByRole('button').filter({ hasText: /^$/ }).nth(3).click();

    const centerX = 500;
    const centerY = 500;
    const dist = 50;
    await page.getByRole('button').filter({ hasText: /^$/ }).nth(6).click();
    await page.mouse.move(centerX - dist, centerY - dist)
    await page.getByRole('button').nth(2).click();
    await page.mouse.move(centerX + dist, centerY + dist)
    // await page.getByRole('button').nth(2).dblclick();
    await page.mouse.click(centerX + dist, centerY + dist)
    await expect(tableMapMarkersPositions).not.toBeVisible();
    await expect(tableMapRectanglesPositions).toBeVisible();
    await expect(tableMapRectanglesPositions).toMatchAriaSnapshot({ name: 'tableMapRectanglesPositions.0.aria.yaml'})
    
    await page.close();
});

