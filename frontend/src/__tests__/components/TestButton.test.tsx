import { describe, test, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'

// Create a simple test component
function TestButton({ onClick, children }: { onClick?: () => void; children: React.ReactNode }) {
    return (
        <button onClick={onClick} data-testid="test-button">
            {children}
        </button>
    )
}

describe('React Component Tests', () => {
    test('should render a button with text', () => {
        render(<TestButton>Click me</TestButton>)

        expect(screen.getByTestId('test-button')).toBeInTheDocument()
        expect(screen.getByText('Click me')).toBeInTheDocument()
    })

    test('should call onClick when button is clicked', () => {
        const mockOnClick = vi.fn()

        render(<TestButton onClick={mockOnClick}>Click me</TestButton>)

        const button = screen.getByTestId('test-button')
        fireEvent.click(button)

        expect(mockOnClick).toHaveBeenCalledOnce()
    })

    test('should render different text content', () => {
        render(<TestButton>Different text</TestButton>)

        expect(screen.getByText('Different text')).toBeInTheDocument()
        expect(screen.queryByText('Click me')).not.toBeInTheDocument()
    })
})
