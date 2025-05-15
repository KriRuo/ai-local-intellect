import React from 'react';
import { render, screen } from '@testing-library/react';
import Dashboard from '../pages/Dashboard';

// Test: Dashboard page
// - Verifies the Dashboard page renders and displays the most recent news heading.
// - Limitation: Only checks for initial render, does not test user interaction, loading, or error states.
// - Recommendation: Add tests for data loading, error handling, and UI interactions.

describe('Dashboard page', () => {
  it('renders without crashing and shows the most recent news heading', () => {
    render(<Dashboard />);
    expect(screen.getByText(/most recent news/i)).toBeInTheDocument();
  });
}); 