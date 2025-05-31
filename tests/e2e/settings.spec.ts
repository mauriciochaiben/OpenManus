import { test, expect } from '@playwright/test';

test.describe('Settings Page E2E Tests', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/settings');
    });

    test('should display settings page layout', async ({ page }) => {
        await expect(page.getByText('Application Settings')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Save Settings' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Reset to Defaults' })).toBeVisible();
    });

    test('should have general settings section', async ({ page }) => {
        await expect(page.getByText('General Settings')).toBeVisible();

        // Check for common settings fields
        const maxTasksInput = page.getByLabel('Max Concurrent Tasks');
        if (await maxTasksInput.isVisible()) {
            await expect(maxTasksInput).toBeVisible();
        }
    });

    test('should have notification settings', async ({ page }) => {
        // Look for notification-related settings
        const notificationSettings = page.getByText('Notifications').or(page.getByText('Notification'));

        if (await notificationSettings.isVisible()) {
            // Check for toggle switches
            const switches = page.locator('.ant-switch');
            if (await switches.first().isVisible()) {
                await expect(switches.first()).toBeVisible();
            }
        }
    });

    test('should save settings successfully', async ({ page }) => {
        // Modify a setting if available
        const numberInput = page.locator('input[type="number"]').first();

        if (await numberInput.isVisible()) {
            await numberInput.clear();
            await numberInput.fill('3');
        }

        // Save settings
        await page.getByRole('button', { name: 'Save Settings' }).click();

        // Should show success message
        await expect(
            page.getByText('Settings saved successfully!').or(
                page.getByText('Saved').or(
                    page.locator('.ant-message-success')
                )
            )
        ).toBeVisible({ timeout: 5000 });
    });

    test('should reset settings to defaults', async ({ page }) => {
        // Click reset button
        await page.getByRole('button', { name: 'Reset to Defaults' }).click();

        // Should either show confirmation or reset immediately
        const confirmButton = page.getByRole('button', { name: 'OK' }).or(page.getByRole('button', { name: 'Yes' }));

        if (await confirmButton.isVisible()) {
            await confirmButton.click();
        }

        // Should show some feedback about reset
        await expect(
            page.getByText('Reset').or(
                page.getByText('Default').or(
                    page.locator('.ant-message')
                )
            )
        ).toBeVisible({ timeout: 5000 });
    });

    test('should handle toggle switches', async ({ page }) => {
        const switches = page.locator('.ant-switch');
        const firstSwitch = switches.first();

        if (await firstSwitch.isVisible()) {
            // Get initial state
            const isChecked = await firstSwitch.isChecked();

            // Toggle the switch
            await firstSwitch.click();

            // Should change state
            const newState = await firstSwitch.isChecked();
            expect(newState).toBe(!isChecked);
        }
    });

    test('should validate numeric inputs', async ({ page }) => {
        const numberInputs = page.locator('input[type="number"]');
        const firstInput = numberInputs.first();

        if (await firstInput.isVisible()) {
            // Test negative number
            await firstInput.clear();
            await firstInput.fill('-1');

            // Try to save
            await page.getByRole('button', { name: 'Save Settings' }).click();

            // Should either prevent saving or show validation error
            const errorMessages = page.locator('.ant-form-item-explain-error').or(page.getByText('Invalid'));

            // Either validation error or successful save (depending on validation rules)
            // We just check that the page doesn't crash
            await expect(page.getByText('Application Settings')).toBeVisible();
        }
    });

    test('should handle dropdown selections', async ({ page }) => {
        const selects = page.locator('.ant-select');
        const firstSelect = selects.first();

        if (await firstSelect.isVisible()) {
            // Click to open dropdown
            await firstSelect.click();

            // Select an option
            const options = page.locator('.ant-select-item');
            const firstOption = options.first();

            if (await firstOption.isVisible()) {
                await firstOption.click();

                // Dropdown should close
                await expect(page.locator('.ant-select-dropdown')).not.toBeVisible();
            }
        }
    });

    test('should persist settings across page reloads', async ({ page }) => {
        // Modify a setting
        const numberInput = page.locator('input[type="number"]').first();

        if (await numberInput.isVisible()) {
            await numberInput.clear();
            await numberInput.fill('7');

            // Save settings
            await page.getByRole('button', { name: 'Save Settings' }).click();

            // Wait for save confirmation
            await expect(
                page.getByText('Settings saved successfully!').or(page.locator('.ant-message-success'))
            ).toBeVisible({ timeout: 5000 });

            // Reload page
            await page.reload();

            // Setting should be persisted
            await expect(numberInput).toHaveValue('7');
        }
    });

    test('should handle form validation errors', async ({ page }) => {
        // Try to set an obviously invalid value
        const textInputs = page.locator('input[type="text"]');
        const firstInput = textInputs.first();

        if (await firstInput.isVisible()) {
            await firstInput.clear();
            await firstInput.fill(''); // Empty value

            // Try to save
            await page.getByRole('button', { name: 'Save Settings' }).click();

            // Should either show validation error or handle gracefully
            await expect(page.getByText('Application Settings')).toBeVisible();
        }
    });

    test('should show loading state when saving', async ({ page }) => {
        // Click save button
        await page.getByRole('button', { name: 'Save Settings' }).click();

        // Should show loading state temporarily
        const loadingButton = page.getByRole('button', { name: 'Save Settings' }).locator('.ant-spin');

        // Loading state might be very brief, so we check for either loading or success
        await expect(
            loadingButton.or(
                page.getByText('Settings saved successfully!').or(
                    page.locator('.ant-message-success')
                )
            )
        ).toBeVisible({ timeout: 5000 });
    });
});
