import React from 'react';
import { render, screen } from '@testing-library/react';
import SavedContent from '../pages/SavedContent';

// Test: SavedContent page
// - Verifies the SavedContent page renders and displays the heading.
// - Limitation: Only checks for initial render, does not test empty state, error state, or user actions.
// - Recommendation: Add tests for empty/error states and user interactions (e.g., removing saved content).

describe('SavedContent page', () => {
  it('renders without crashing and shows the Saved Content heading', () => {
    render(<SavedContent />);
    expect(screen.getByText(/saved content/i)).toBeInTheDocument();
  });
}); 