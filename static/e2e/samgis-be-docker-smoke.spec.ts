import { test, expect } from '@playwright/test';

const BASE = process.env.SMOKE_URL ?? '';

async function hasBackend(baseURL: string): Promise<boolean> {
    try {
        const res = await fetch(`${baseURL}/health`, { signal: AbortSignal.timeout(2000) });
        if (!res.ok) return false;
        const body = await res.json();
        return typeof body.msg === 'string';
    } catch {
        return false;
    }
}

test('smoke test - frontend loads without JS errors', async ({ page, baseURL }) => {
    const url = BASE || baseURL!;
    const jsErrors: string[] = [];
    const failedRequests: string[] = [];

    page.on('pageerror', err => jsErrors.push(err.message));
    page.on('response', response => {
        if (response.status() >= 400) {
            failedRequests.push(`${response.status()} ${response.url()}`);
        }
    });

    const response = await page.goto(url, { waitUntil: 'networkidle' });
    expect(response?.status()).toBe(200);

    if (failedRequests.length > 0) {
        console.log('FAILED REQUESTS:');
        failedRequests.forEach(r => console.log('  -', r));
    }
    if (jsErrors.length > 0) {
        console.log('JS ERRORS:');
        jsErrors.forEach(e => console.log('  -', e));
    }

    // Tour dialog proves Vue + Leaflet + driver.js all loaded
    await expect(page.getByRole('dialog', { name: 'SamGIS' })).toBeVisible();

    // Dismiss tour
    await page.locator('body').press('Escape');

    // Map container rendered
    await expect(page.getByTestId('map-container')).toBeVisible();

    // Send button present and disabled (no prompts yet)
    await expect(page.getByRole('button', { name: 'Empty prompt (disabled)' })).toBeDisabled();

    // Footer branding visible (text varies by VITE__MODEL_VARIANT)
    await expect(page.getByText(/ML predictions powered by|predictions made with a machine learning model/)).toBeVisible();

    expect(failedRequests).toEqual([]);
    expect(jsErrors).toEqual([]);
});

test('smoke test - health endpoint returns 200', async ({ baseURL }) => {
    const url = BASE || baseURL!;
    const backend = await hasBackend(url);
    test.skip(!backend, 'backend not reachable');
    const response = await fetch(`${url}/health`);
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.msg).toContain('still alive');
});

test('smoke test - infer_samgis rejects empty body with 422', async ({ baseURL }) => {
    const url = BASE || baseURL!;
    const backend = await hasBackend(url);
    test.skip(!backend, 'backend not reachable');
    const response = await fetch(`${url}/infer_samgis`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({}),
    });
    expect(response.status).toBe(422);
    const body = await response.json();
    expect(body.msg).toContain('Unprocessable Entity');
});
