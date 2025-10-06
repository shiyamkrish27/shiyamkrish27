import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Home from './page';

// Mock fetch for API routes
const mockFetch = vi.fn();

describe('Home Task Tracker', () => {
  beforeAll(() => {
    // @ts-expect-error override
    global.fetch = mockFetch;
  });

  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('renders header and empty list', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
    render(<Home />);
    expect(await screen.findByText('Task Tracker')).toBeInTheDocument();
  });

  it('adds a task via POST and refreshes', async () => {
    mockFetch
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 1, title: 'Test', completed: false, createdAt: '', updatedAt: '' }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ([{ id: 1, title: 'Test', completed: false, createdAt: '', updatedAt: '' }]) });

    render(<Home />);

    const input = await screen.findByPlaceholderText('Add a task...');
    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/tasks', expect.objectContaining({ method: 'POST' }));
    });

    expect(await screen.findByText('Test')).toBeInTheDocument();
  });
});
