export type SchoolSummary = {
  officeCode: string;
  schoolCode: string;
  name: string;
  region: string;
  schoolType: string;
};

export type SchoolSearchResponse = {
  items: SchoolSummary[];
  total: number;
  hasMore: boolean;
};

export type MenuItem = {
  name: string;
  allergyCodes: string[];
};

export type Measurement = {
  label: string;
  value: number;
  unit: string;
  sourceText: string;
};

export type Meal = {
  date: string;
  mealType: string;
  menu: MenuItem[];
  calories?: Measurement;
  nutrients: Measurement[];
  nutritionText?: string;
  origin?: string;
};

export type MealResponse = { items: Meal[] };
export type ApiError = { code: string; message: string; details?: unknown[] };

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function request<T>(path: string, params: URLSearchParams): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}?${params.toString()}`);
  if (!response.ok) {
    const payload = (await response.json()) as { detail?: ApiError };
    throw payload.detail ?? { code: 'INTERNAL_ERROR', message: '요청을 처리하지 못했습니다.' };
  }
  return (await response.json()) as T;
}

export function searchSchools(name: string): Promise<SchoolSearchResponse> {
  return request('/api/v1/schools', new URLSearchParams({ name }));
}

export function fetchMeals(params: { officeCode: string; schoolCode: string; from: string; to: string }): Promise<MealResponse> {
  return request('/api/v1/meals', new URLSearchParams(params));
}
