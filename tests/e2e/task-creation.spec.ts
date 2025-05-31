import { test, expect } from '@playwright/test';

test.describe('Task Creation E2E Tests', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');

        // Open task creation form
        await page.getByRole('button', { name: 'Create Task' }).click();
        await expect(page.getByText('Create New Task')).toBeVisible();
    });

    test('should create a simple task successfully', async ({ page }) => {
        // Fill out task form
        await page.getByPlaceholder('Enter a clear, descriptive title').fill('Test Task - E2E');
        await page.getByPlaceholder('Describe what you want to accomplish').fill('This is a test task created via E2E testing to verify the task creation workflow.');

        // Select mode
        await page.getByRole('combobox', { name: 'Execution Mode' }).click();
        await page.getByText('Single Agent').click();

        // Submit form
        await page.getByRole('button', { name: 'Create Task' }).click();

        // Should show loading state
        await expect(page.getByText('Creating...')).toBeVisible();

        // Should navigate to task detail page or show success
        await expect(page.getByText('Task created successfully!').or(page.getByText('Task Details'))).toBeVisible({ timeout: 10000 });
    });

    test('should validate required fields', async ({ page }) => {
        // Try to submit without filling required fields
        await page.getByRole('button', { name: 'Create Task' }).click();

        // Should show validation errors
        await expect(page.getByText('Please enter a task title')).toBeVisible();
        await expect(page.getByText('Please enter a task description')).toBeVisible();
    });

    test('should handle document upload', async ({ page }) => {
        // Fill basic information
        await page.getByPlaceholder('Enter a clear, descriptive title').fill('Document Test Task');
        await page.getByPlaceholder('Describe what you want to accomplish').fill('Testing document upload functionality.');

        // Check if document upload area is present
        const uploadArea = page.locator('[data-testid="document-upload"]').or(page.getByText('Click or drag files to upload'));
        if (await uploadArea.isVisible()) {
            // Create a test file and upload
            const testFile = await page.evaluateHandle(() => {
                const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
                return file;
            });

            // Upload the file
            await page.setInputFiles('input[type="file"]', await testFile.jsonValue());

            // Verify file appears in the upload list
            await expect(page.getByText('test.txt')).toBeVisible();
        }

        // Submit form
        await page.getByRole('button', { name: 'Create Task' }).click();
    });

    test('should handle different execution modes', async ({ page }) => {
        // Fill basic information
        await page.getByPlaceholder('Enter a clear, descriptive title').fill('Multi-Agent Test Task');
        await page.getByPlaceholder('Describe what you want to accomplish').fill('Testing multi-agent execution mode.');

        // Test different execution modes
        const modes = ['Auto Agent Selection', 'Single Agent', 'Multi-Agent'];

        for (const mode of modes) {
            await page.getByRole('combobox', { name: 'Execution Mode' }).click();
            await page.getByText(mode).click();

            // Verify mode is selected
            await expect(page.getByRole('combobox', { name: 'Execution Mode' })).toContainText(mode);
        }
    });

    test('should close task creation form', async ({ page }) => {
        // Should be able to close the form
        const closeButton = page.getByRole('button', { name: 'Cancel' }).or(page.getByRole('button', { name: '×' }));

        if (await closeButton.isVisible()) {
            await closeButton.click();

            // Should return to home page
            await expect(page.getByText('Welcome to OpenManus')).toBeVisible();
        }
    });

    test('should handle form validation edge cases', async ({ page }) => {
        // Test very long title
        const longTitle = 'A'.repeat(200);
        await page.getByPlaceholder('Enter a clear, descriptive title').fill(longTitle);

        // Test very long description
        const longDescription = 'B'.repeat(2000);
        await page.getByPlaceholder('Describe what you want to accomplish').fill(longDescription);

        // Should either accept it or show appropriate validation
        await page.getByRole('button', { name: 'Create Task' }).click();

        // Wait for either success or validation error
        await expect(
            page.getByText('Creating...').or(
                page.getByText('Title is too long').or(
                    page.getByText('Description is too long')
                )
            )
        ).toBeVisible({ timeout: 5000 });
    });
});
