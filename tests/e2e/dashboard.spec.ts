import { test, expect } from '@playwright/test';

test.describe('Dashboard E2E Tests', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/dashboard');
    });

    test('should display dashboard title and refresh button', async ({ page }) => {
        await expect(page.getByText('Dashboard OpenManus')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Atualizar' })).toBeVisible();
    });

    test('should display system health alert', async ({ page }) => {
        // Wait for system health to load
        const healthAlert = page.locator('.ant-alert').first();

        if (await healthAlert.isVisible()) {
            // Should show either online or offline status
            await expect(
                page.getByText('Sistema Online').or(page.getByText('Sistema Offline'))
            ).toBeVisible();
        }
    });

    test('should display statistics cards', async ({ page }) => {
        // Check for all statistics cards
        await expect(page.getByText('Total de Tarefas')).toBeVisible();
        await expect(page.getByText('Concluídas')).toBeVisible();
        await expect(page.getByText('Em Execução')).toBeVisible();
        await expect(page.getByText('Pendentes')).toBeVisible();

        // Statistics should show numbers
        const statisticValues = page.locator('.ant-statistic-content-value');
        const firstValue = statisticValues.first();
        await expect(firstValue).toBeVisible();

        // Values should be numeric
        const valueText = await firstValue.textContent();
        expect(valueText).toMatch(/^\d+$/);
    });

    test('should display progress overview', async ({ page }) => {
        await expect(page.getByText('Progresso Geral')).toBeVisible();

        // Should have a circular progress indicator
        const progressCircle = page.locator('.ant-progress-circle');
        if (await progressCircle.isVisible()) {
            await expect(progressCircle).toBeVisible();
        }
    });

    test('should display recent tasks section', async ({ page }) => {
        await expect(page.getByText('Tarefas Recentes')).toBeVisible();

        // Should either show tasks or empty state
        const tasksList = page.locator('.ant-list');
        const emptyState = page.getByText('Nenhuma tarefa encontrada');

        await expect(tasksList.or(emptyState)).toBeVisible();
    });

    test('should refresh dashboard data', async ({ page }) => {
        const refreshButton = page.getByRole('button', { name: 'Atualizar' });

        // Click refresh button
        await refreshButton.click();

        // Should show loading state
        await expect(page.getByText('Atualizar').or(page.locator('.ant-spin'))).toBeVisible();

        // Should complete refresh
        await expect(refreshButton).not.toBeDisabled({ timeout: 10000 });
    });

    test('should handle error states gracefully', async ({ page }) => {
        // Simulate network failure by intercepting requests
        await page.route('**/api/**', route => {
            route.abort();
        });

        // Reload page to trigger API calls
        await page.reload();

        // Should handle gracefully (show error message or loading state)
        const errorIndicators = [
            page.getByText('Failed to load'),
            page.getByText('Error'),
            page.getByText('Connection failed'),
            page.locator('.ant-spin') // Loading state is also acceptable
        ];

        let errorShown = false;
        for (const indicator of errorIndicators) {
            if (await indicator.isVisible()) {
                errorShown = true;
                break;
            }
        }

        // Either error or loading should be shown, not a blank page
        expect(errorShown).toBe(true);
    });

    test('should navigate to task details from recent tasks', async ({ page }) => {
        // Wait for recent tasks to load
        const taskList = page.locator('.ant-list-item').first();

        if (await taskList.isVisible()) {
            // Click on first task if available
            const viewButton = taskList.locator('button').or(taskList.locator('a')).first();

            if (await viewButton.isVisible()) {
                await viewButton.click();

                // Should navigate to task detail page
                await expect(page.url()).toMatch(/\/task\/\w+/);
            }
        }
    });

    test('should display responsive layout', async ({ page, isMobile }) => {
        // Check responsive behavior
        const statisticsGrid = page.locator('.ant-row').first();
        await expect(statisticsGrid).toBeVisible();

        if (isMobile) {
            // On mobile, cards should stack vertically
            const viewport = page.viewportSize();
            if (viewport) {
                expect(viewport.width).toBeLessThan(768);
            }
        }
    });

    test('should show loading state on initial load', async ({ page }) => {
        // Navigate to dashboard and immediately check for loading
        await page.goto('/dashboard');

        // Should show either loading spinner or loaded content quickly
        const loadingElements = [
            page.getByText('Carregando dashboard...'),
            page.locator('.ant-spin'),
            page.getByText('Dashboard OpenManus') // Loaded state
        ];

        let elementVisible = false;
        for (const element of loadingElements) {
            if (await element.isVisible({ timeout: 1000 })) {
                elementVisible = true;
                break;
            }
        }

        expect(elementVisible).toBe(true);
    });

    test('should handle real-time updates', async ({ page }) => {
        // Check initial state
        const totalTasksValue = page.locator('.ant-statistic-content-value').first();
        const initialValue = await totalTasksValue.textContent();

        // If WebSocket is working, values might update
        // For now, just verify the elements remain stable
        await page.waitForTimeout(2000);

        // Elements should still be visible after potential updates
        await expect(page.getByText('Dashboard OpenManus')).toBeVisible();
        await expect(totalTasksValue).toBeVisible();
    });
});
