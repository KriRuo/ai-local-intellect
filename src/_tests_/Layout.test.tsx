import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Layout } from '../components/Layout';

// Test: Layout component
// - Verifies the Layout component renders its children.
// - Limitation: Only checks for rendering children, does not test layout structure, navigation, or responsiveness.
// - Recommendation: Add tests for layout structure, navigation links, and responsive behavior.

describe('Layout component', () => {
  it('renders children', () => {
    render(
      <MemoryRouter>
        <Layout><div>Test Child</div></Layout>
      </MemoryRouter>
    );
    expect(screen.getByText('Test Child')).toBeInTheDocument();
  });
}); 