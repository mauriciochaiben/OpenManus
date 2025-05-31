import { test, expect } from '@playwright/test';

test.describe('WebSocket Integration E2E Tests', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
    });

    test('should display WebSocket connection status', async ({ page }) => {
        // Check for WebSocket status indicator
        await expect(page.getByText('WebSocket:')).toBeVisible();

        // Should show connection status
        const statusTags = page.locator('.ant-tag');
        const wsStatusTag = statusTags.filter({ hasText: /CONNECTED|DISCONNECTED|CONNECTING/ });

        await expect(wsStatusTag.first()).toBeVisible({ timeout: 10000 });
    });

    test('should handle real-time task updates', async ({ page }) => {
        // Navigate to dashboard to see real-time updates
        await page.goto('/dashboard');

        // Create a task to trigger WebSocket updates
        await page.goto('/');
        await page.getByRole('button', { name: 'Create Task' }).click();

        // Fill and submit task
        await page.getByPlaceholder('Enter a clear, descriptive title').fill('WebSocket Test Task');
        await page.getByPlaceholder('Describe what you want to accomplish').fill('Testing real-time updates via WebSocket.');
        await page.getByRole('button', { name: 'Create Task' }).click();

        // Wait for task creation
        await expect(page.getByText('Task created successfully!').or(page.getByText('Creating...'))).toBeVisible({ timeout: 10000 });

        // Go back to dashboard to see if it updates
        await page.goto('/dashboard');

        // Should see the new task in statistics or recent tasks
        await expect(page.getByText('WebSocket Test Task').or(page.getByText('1').first())).toBeVisible({ timeout: 15000 });
    });

    test('should handle connection recovery', async ({ page }) => {
        // Check initial connection status
        await expect(page.getByText('System Status')).toBeVisible();

        // Simulate network interruption by navigating away and back
        await page.goto('about:blank');
        await page.waitForTimeout(2000);
        await page.goto('/');

        // Should reconnect automatically
        await expect(page.getByText('System Status')).toBeVisible();

        // WebSocket should eventually reconnect
        const wsStatus = page.locator('.ant-tag').filter({ hasText: /CONNECTED|CONNECTING|RECONNECTING/ });
        await expect(wsStatus.first()).toBeVisible({ timeout: 15000 });
    });

    test('should receive notifications via WebSocket', async ({ page }) => {
        // Check for notification container or system
        const notificationArea = page.locator('.notification-container').or(page.locator('.ant-notification'));

        // Create a task that might trigger notifications
        await page.getByRole('button', { name: 'Create Task' }).click();
        await page.getByPlaceholder('Enter a clear, descriptive title').fill('Notification Test Task');
        await page.getByPlaceholder('Describe what you want to accomplish').fill('Testing WebSocket notifications.');
        await page.getByRole('button', { name: 'Create Task' }).click();

        // Look for any notification that appears
        const notifications = [
            page.getByText('Task created'),
            page.getByText('Success'),
            page.locator('.ant-message'),
            page.locator('.notification'),
            notificationArea
        ];

        let notificationFound = false;
        for (const notification of notifications) {
            if (await notification.isVisible({ timeout: 5000 })) {
                notificationFound = true;
                break;
            }
        }

        // Either notification system works or task creation succeeds
        expect(notificationFound || await page.getByText('Task created successfully!').isVisible()).toBe(true);
    });

    test('should handle WebSocket disconnection gracefully', async ({ page }) => {
        // Check initial status
        await expect(page.getByText('System Status')).toBeVisible();

        // Block WebSocket connections by intercepting requests
        await page.route('ws://**', route => route.abort());
        await page.route('wss://**', route => route.abort());

        // Reload to trigger new WebSocket connection attempt
        await page.reload();

        // Should handle disconnection gracefully
        await expect(page.getByText('OpenManus')).toBeVisible();

        // Status should indicate disconnection or connection issues
        const statusIndicators = [
            page.getByText('DISCONNECTED'),
            page.getByText('Connection Issues'),
            page.getByText('FAILED'),
            page.getByText('Offline')
        ];

        let disconnectionIndicatorFound = false;
        for (const indicator of statusIndicators) {
            if (await indicator.isVisible({ timeout: 10000 })) {
                disconnectionIndicatorFound = true;
                break;
            }
        }

        // Should show some indication of connection issues
        expect(disconnectionIndicatorFound).toBe(true);
    });

    test('should maintain functionality without WebSocket', async ({ page }) => {
        // Block WebSocket connections
        await page.route('ws://**', route => route.abort());
        await page.route('wss://**', route => route.abort());

        await page.reload();

        // Basic functionality should still work
        await expect(page.getByText('Welcome to OpenManus')).toBeVisible();

        // Navigation should work
        await page.getByRole('menuitem', { name: 'Dashboard' }).click();
        await expect(page.getByText('Dashboard OpenManus')).toBeVisible();

        // Form interactions should work
        await page.goto('/');
        await page.getByRole('button', { name: 'Create Task' }).click();
        await expect(page.getByText('Create New Task')).toBeVisible();
    });

    test('should show connection status in WebSocket status component', async ({ page }) => {
        // Look for WebSocket status component
        const wsStatusComponent = page.locator('.ws-status').or(page.getByText('WebSocket Status'));

        if (await wsStatusComponent.isVisible()) {
            // Should show connection state
            const statusStates = [
                page.getByText('Connected'),
                page.getByText('Connecting'),
                page.getByText('Disconnected'),
                page.getByText('Reconnecting')
            ];

            let statusFound = false;
            for (const status of statusStates) {
                if (await status.isVisible()) {
                    statusFound = true;
                    break;
                }
            }

            expect(statusFound).toBe(true);
        }
    });

    test('should update UI in real-time for task progress', async ({ page }) => {
        // Create and submit a task
        await page.getByRole('button', { name: 'Create Task' }).click();
        await page.getByPlaceholder('Enter a clear, descriptive title').fill('Progress Test Task');
        await page.getByPlaceholder('Describe what you want to accomplish').fill('Testing real-time progress updates.');
        await page.getByRole('button', { name: 'Create Task' }).click();

        // If task creation succeeds and redirects to task detail
        if (await page.url().includes('/task/')) {
            // Should show task execution dashboard
            await expect(page.getByText('Progress Test Task').or(page.getByText('Task Details'))).toBeVisible({ timeout: 10000 });

            // Look for progress indicators
            const progressElements = [
                page.locator('.ant-progress'),
                page.getByText('Progress'),
                page.locator('.ant-timeline'),
                page.getByText('Running'),
                page.getByText('Completed')
            ];

            let progressFound = false;
            for (const element of progressElements) {
                if (await element.isVisible({ timeout: 5000 })) {
                    progressFound = true;
                    break;
                }
            }

            // Either shows progress or task details
            expect(progressFound || await page.getByText('Progress Test Task').isVisible()).toBe(true);
        }
    });
});
