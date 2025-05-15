// Test: App root component
// - Verifies the App renders and shows the dashboard by default.
// - Limitation: Only checks for initial render, does not test navigation, error states, or user interaction.
// - Recommendation: Add tests for navigation, error handling, and user flows.
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App root', () => {
  it('renders without crashing and shows dashboard route by default', () => {
    render(<App />);
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
  });
}); 