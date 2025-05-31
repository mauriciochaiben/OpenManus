import { test, expect } from '@playwright/test';

test.describe('Home Page E2E Tests', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to the home page
        await page.goto('/');
    });

    test('should display welcome message and navigation', async ({ page }) => {
        // Check page title
        await expect(page).toHaveTitle(/OpenManus/);

        // Check welcome message
        await expect(page.getByText('Welcome to OpenManus')).toBeVisible();
        await expect(page.getByText('Create and manage your AI-powered tasks')).toBeVisible();

        // Check navigation sidebar
        await expect(page.getByText('Home')).toBeVisible();
        await expect(page.getByText('Dashboard')).toBeVisible();
        await expect(page.getByText('AI Chat')).toBeVisible();
        await expect(page.getByText('MCP Config')).toBeVisible();
        await expect(page.getByText('Settings')).toBeVisible();
    });

    test('should display system status card', async ({ page }) => {
        // Wait for system status to load
        await expect(page.getByText('System Status')).toBeVisible();

        // Check for status indicators
        await expect(page.getByText('Backend Server:')).toBeVisible();
        await expect(page.getByText('REST API:')).toBeVisible();
        await expect(page.getByText('WebSocket:')).toBeVisible();
    });

    test('should display task statistics cards', async ({ page }) => {
        // Check for statistics cards
        await expect(page.getByText('Running Tasks')).toBeVisible();
        await expect(page.getByText('Completed Tasks')).toBeVisible();
        await expect(page.getByText('Pending Tasks')).toBeVisible();
        await expect(page.getByText('Total Tasks')).toBeVisible();
    });

    test('should navigate to create task form', async ({ page }) => {
        // Click create task button
        await page.getByRole('button', { name: 'Create Task' }).click();

        // Should show task creation form
        await expect(page.getByText('Create New Task')).toBeVisible();
        await expect(page.getByPlaceholder('Enter a clear, descriptive title')).toBeVisible();
    });

    test('should navigate to chat page', async ({ page }) => {
        // Click AI Chat button
        await page.getByRole('button', { name: 'AI Chat' }).click();

        // Should navigate to chat page
        await expect(page.url()).toContain('/chat');
        await expect(page.getByText('AI Chat - OpenManus')).toBeVisible();
    });

    test('should navigate between pages using sidebar', async ({ page }) => {
        // Navigate to Dashboard
        await page.getByRole('menuitem', { name: 'Dashboard' }).click();
        await expect(page.url()).toContain('/dashboard');
        await expect(page.getByText('Dashboard OpenManus')).toBeVisible();

        // Navigate to Settings
        await page.getByRole('menuitem', { name: 'Settings' }).click();
        await expect(page.url()).toContain('/settings');
        await expect(page.getByText('Application Settings')).toBeVisible();

        // Navigate back to Home
        await page.getByRole('menuitem', { name: 'Home' }).click();
        await expect(page.url()).toBe('http://localhost:3000/');
    });

    test('should handle responsive design', async ({ page, isMobile }) => {
        if (isMobile) {
            // On mobile, sidebar should be collapsed or hidden
            const sidebar = page.locator('.sidebar');
            const sidebarBox = await sidebar.boundingBox();

            // Sidebar should either be hidden or have reduced width
            if (sidebarBox) {
                expect(sidebarBox.width).toBeLessThan(250);
            }
        } else {
            // On desktop, sidebar should be visible
            await expect(page.locator('.sidebar')).toBeVisible();
        }
    });
});
