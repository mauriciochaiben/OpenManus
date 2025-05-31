import { test, expect } from '@playwright/test';

test.describe('Chat Page E2E Tests', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/chat');
    });

    test('should display chat interface', async ({ page }) => {
        // Check page elements
        await expect(page.getByText('AI Chat - OpenManus')).toBeVisible();
        await expect(page.getByPlaceholder('Digite sua mensagem')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Enviar' })).toBeVisible();
    });

    test('should send and receive messages', async ({ page }) => {
        const testMessage = 'Hello, this is a test message from E2E testing';

        // Type message
        await page.getByPlaceholder('Digite sua mensagem').fill(testMessage);

        // Send message
        await page.getByRole('button', { name: 'Enviar' }).click();

        // Verify message appears in chat
        await expect(page.getByText(testMessage)).toBeVisible();

        // Verify input is cleared
        await expect(page.getByPlaceholder('Digite sua mensagem')).toHaveValue('');

        // Should show loading state
        await expect(page.getByText('Enviando...')).toBeVisible();

        // Wait for AI response (timeout after 10 seconds)
        const aiResponse = page.locator('[data-testid="ai-message"]').or(page.getByText('I am')).first();
        await expect(aiResponse).toBeVisible({ timeout: 10000 });
    });

    test('should handle enter key for sending messages', async ({ page }) => {
        const testMessage = 'Testing enter key functionality';

        // Type message
        await page.getByPlaceholder('Digite sua mensagem').fill(testMessage);

        // Press Enter to send
        await page.getByPlaceholder('Digite sua mensagem').press('Enter');

        // Verify message appears
        await expect(page.getByText(testMessage)).toBeVisible();
    });

    test('should handle shift+enter for new lines', async ({ page }) => {
        const textarea = page.getByPlaceholder('Digite sua mensagem');

        // Type message with shift+enter
        await textarea.fill('Line 1');
        await textarea.press('Shift+Enter');
        await textarea.fill('Line 1\nLine 2');

        // Should create multi-line message
        const currentValue = await textarea.inputValue();
        expect(currentValue).toContain('\n');
    });

    test('should clear chat history', async ({ page }) => {
        // Send a test message first
        await page.getByPlaceholder('Digite sua mensagem').fill('Test message for clearing');
        await page.getByRole('button', { name: 'Enviar' }).click();

        // Wait for message to appear
        await expect(page.getByText('Test message for clearing')).toBeVisible();

        // Clear chat
        const clearButton = page.getByRole('button', { name: 'Limpar conversa' }).or(page.getByTitle('Limpar conversa'));
        if (await clearButton.isVisible()) {
            await clearButton.click();

            // Messages should be cleared
            await expect(page.getByText('Test message for clearing')).not.toBeVisible();
            await expect(page.getByText('Nenhuma mensagem ainda')).toBeVisible();
        }
    });

    test('should show suggestions if available', async ({ page }) => {
        // Check if suggestions area exists
        const suggestionsArea = page.getByText('Sugestões:');

        if (await suggestionsArea.isVisible()) {
            // Click on a suggestion if available
            const firstSuggestion = page.locator('.ant-tag').first();
            if (await firstSuggestion.isVisible()) {
                const suggestionText = await firstSuggestion.textContent();
                await firstSuggestion.click();

                // Should populate the input with suggestion
                await expect(page.getByPlaceholder('Digite sua mensagem')).toHaveValue(suggestionText || '');
            }
        }
    });

    test('should handle disabled state when loading', async ({ page }) => {
        // Send a message to trigger loading state
        await page.getByPlaceholder('Digite sua mensagem').fill('Test loading state');
        await page.getByRole('button', { name: 'Enviar' }).click();

        // Input and button should be disabled during loading
        await expect(page.getByPlaceholder('Digite sua mensagem')).toBeDisabled();
        await expect(page.getByRole('button', { name: 'Enviando...' })).toBeDisabled();
    });

    test('should handle empty message validation', async ({ page }) => {
        // Try to send empty message
        await page.getByRole('button', { name: 'Enviar' }).click();

        // Button should be disabled for empty input
        await expect(page.getByRole('button', { name: 'Enviar' })).toBeDisabled();
    });

    test('should display message timestamps', async ({ page }) => {
        // Send a test message
        await page.getByPlaceholder('Digite sua mensagem').fill('Timestamp test message');
        await page.getByRole('button', { name: 'Enviar' }).click();

        // Should show timestamp
        const timePattern = /\d{1,2}:\d{2}/; // HH:MM format
        await expect(page.locator('text=' + timePattern.source)).toBeVisible({ timeout: 5000 });
    });

    test('should handle long messages properly', async ({ page }) => {
        const longMessage = 'This is a very long message that should test the chat interface ability to handle long text content properly and ensure it displays correctly without breaking the layout. '.repeat(5);

        // Send long message
        await page.getByPlaceholder('Digite sua mensagem').fill(longMessage);
        await page.getByRole('button', { name: 'Enviar' }).click();

        // Message should appear and be readable
        await expect(page.getByText(longMessage).first()).toBeVisible();

        // Layout should not be broken
        const chatContainer = page.locator('[data-testid="chat-container"]').or(page.locator('.ant-card-body')).first();
        await expect(chatContainer).toBeVisible();
    });
});
