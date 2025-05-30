import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App'; // Assuming your main App component is in App.tsx

test('renders learn react link', () => {
    render(<App />);
    // Example: Check if a known text element is present
    // const linkElement = screen.getByText(/learn react/i);
    // expect(linkElement).toBeInTheDocument();
    // Replace with a more relevant test for your application
    expect(screen.getByText(/OpenManus/i)).toBeInTheDocument();
});
