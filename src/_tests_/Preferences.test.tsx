import React from 'react';
import { render, screen } from '@testing-library/react';
import Preferences from '../pages/Preferences';

// Test: Preferences page
// - Verifies the Preferences page renders and shows loading state.
// - Limitation: Only checks for loading state, does not test preferences loaded, error, or user interaction.
// - Recommendation: Add tests for loaded state, error handling, and user actions.

describe('Preferences page', () => {
  it('renders without crashing and shows loading state', () => {
    render(<Preferences />);
    expect(screen.getByText(/loading preferences/i)).toBeInTheDocument();
  });
});
