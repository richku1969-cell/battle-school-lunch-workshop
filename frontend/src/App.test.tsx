import { beforeEach, describe, expect, it, vi } from 'vitest';
import React from 'react';

vi.mock('@fluentui/react-components', () => {
  return {
    Button: ({ children, ...props }: any) => React.createElement('button', props, children),
    Card: ({ children, className }: any) => React.createElement('div', { className }, children),
    Input: ({ ...props }: any) => React.createElement('input', props),
    MessageBar: ({ children }: any) => React.createElement('div', {}, children),
    MessageBarBody: ({ children }: any) => React.createElement('div', {}, children),
    Spinner: ({ label }: any) => React.createElement('div', {}, label),
    Text: ({ children, ...props }: any) => React.createElement('span', props, children),
    makeStyles: () => () => ({}),
    tokens: { borderRadiusXLarge: '24px', colorBrandStroke1: '#0f6cbd' },
  };
});

import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { App } from './App';

const fetchMock = vi.fn();
vi.stubGlobal('fetch', fetchMock);

function renderApp() {
  render(<App />);
}

describe('App', () => {
  beforeEach(() => {
    fetchMock.mockReset();
    document.body.innerHTML = '';
  });

  it('searches, selects a school, and shows meals', async () => {
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [{ officeCode: 'B10', schoolCode: '7010569', name: '테스트고', region: '서울', schoolType: '고등학교' }],
          total: 1,
          hasMore: false,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          items: [
            {
              date: '2026-08-14',
              mealType: '중식',
              menu: [{ name: '카레라이스', allergyCodes: ['2'] }],
              calories: { label: '열량', value: 531.2, unit: 'kcal', sourceText: '열량 : 531.2 kcal' },
              nutrients: [],
              nutritionText: '탄수화물 : 30.5 g<br/>단백질 : 10.2 g',
              origin: '쌀 : 국내산<br/>배추 : 국내산<br/>비고 : ',
            },
          ],
        }),
      });

    renderApp();

    fireEvent.change(screen.getByLabelText('학교명 검색어'), { target: { value: '테스트' } });
    fireEvent.click(screen.getByRole('button', { name: '검색' }));

    await screen.findByText('테스트고');
    fireEvent.click(screen.getByRole('button', { name: /테스트고/ }));
    fireEvent.click(screen.getByRole('button', { name: '급식 조회' }));

    await screen.findByText(/카레라이스/);
    expect(screen.getByText('열량 : 531.2 kcal')).toBeInTheDocument();
    expect(screen.getByText('탄수화물 : 30.5 g')).toBeInTheDocument();
    expect(screen.getByText('쌀 : 국내산')).toBeInTheDocument();
    expect(screen.queryByText('비고 :')).not.toBeInTheDocument();
  });

  it('blocks invalid date ranges', async () => {
    renderApp();
    fireEvent.change(screen.getAllByLabelText('시작일')[0], { target: { value: '2026-08-20' } });
    fireEvent.change(screen.getAllByLabelText('종료일')[0], { target: { value: '2026-08-10' } });
    await waitFor(() => expect(screen.getByText('시작일은 종료일보다 늦을 수 없습니다.')).toBeInTheDocument());
  });

  it('shows empty school result message', async () => {
    fetchMock.mockResolvedValueOnce({ ok: true, json: async () => ({ items: [], total: 0, hasMore: false }) });
    renderApp();
    fireEvent.change(screen.getByLabelText('학교명 검색어'), { target: { value: '없는학교' } });
    fireEvent.click(screen.getByRole('button', { name: '검색' }));
    await screen.findByText('일치하는 학교가 없습니다. 검색어를 더 구체적으로 입력해 주세요.');
  });
});
