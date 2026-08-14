import {
  Button,
  Card,
  Input,
  MessageBar,
  MessageBarBody,
  Spinner,
  Text,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import type { ApiError, Meal, SchoolSummary } from './api';
import { fetchMeals, searchSchools } from './api';

const useStyles = makeStyles({
  page: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #eff6ff 0%, #f8fafc 48%, #ecfeff 100%)',
    padding: '32px 16px 48px',
  },
  shell: {
    width: 'min(1120px, 100%)',
    margin: '0 auto',
    display: 'grid',
    gap: '20px',
  },
  hero: {
    padding: '24px',
    borderRadius: tokens.borderRadiusXLarge,
    backgroundColor: 'rgba(255,255,255,0.62)',
    backdropFilter: 'blur(18px)',
    border: '1px solid rgba(255,255,255,0.7)',
    boxShadow: '0 16px 40px rgba(15, 23, 42, 0.08)',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '20px',
  },
  card: {
    backgroundColor: 'rgba(255,255,255,0.56)',
    backdropFilter: 'blur(16px)',
    border: '1px solid rgba(255,255,255,0.75)',
    boxShadow: '0 12px 28px rgba(15, 23, 42, 0.08)',
    padding: '20px',
  },
  sectionTitle: {
    marginBottom: '12px',
  },
  field: {
    display: 'grid',
    gap: '6px',
  },
  searchRow: {
    display: 'flex',
    gap: '8px',
    alignItems: 'end',
  },
  input: {
    width: '100%',
  },
  schoolList: {
    display: 'grid',
    gap: '8px',
    marginTop: '12px',
  },
  schoolButton: {
    textAlign: 'left',
    justifyContent: 'flex-start',
    height: 'auto',
    padding: '12px',
  },
  selectedSchool: {
    border: `1px solid ${tokens.colorBrandStroke1}`,
  },
  dateGrid: {
    display: 'grid',
    gap: '12px',
    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
    alignItems: 'end',
  },
  resultList: {
    display: 'grid',
    gap: '16px',
  },
  menuList: {
    margin: 0,
    paddingLeft: '20px',
  },
  chartWrap: {
    width: '100%',
    height: '280px',
  },
});

const today = new Date();
const defaultTo = today.toISOString().slice(0, 10);
const defaultFrom = new Date(today.getTime() - 6 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
const MAX_RANGE_DAYS = 31;

function formatDate(value: string): string {
  const date = new Date(`${value}T00:00:00+09:00`);
  return new Intl.DateTimeFormat('ko-KR', { dateStyle: 'long' }).format(date);
}

export function App() {
  const styles = useStyles();
  const [query, setQuery] = useState('');
  const [schools, setSchools] = useState<SchoolSummary[]>([]);
  const [selectedSchool, setSelectedSchool] = useState<SchoolSummary | null>(null);
  const [fromDate, setFromDate] = useState(defaultFrom);
  const [toDate, setToDate] = useState(defaultTo);
  const [meals, setMeals] = useState<Meal[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [mealLoading, setMealLoading] = useState(false);
  const [searchError, setSearchError] = useState<ApiError | null>(null);
  const [mealError, setMealError] = useState<ApiError | null>(null);
  const [searchMeta, setSearchMeta] = useState<{ total: number; hasMore: boolean } | null>(null);

  const chartGroups = useMemo(() => {
    const grouped = new Map<string, { key: string; label: string; unit: string; values: Array<{ date: string; value: number }> }>();
    meals.forEach((meal) => {
      const measurements = [...(meal.calories ? [meal.calories] : []), ...meal.nutrients];
      measurements.forEach((measurement) => {
        const key = `${measurement.label}-${measurement.unit}`;
        const group = grouped.get(key) ?? { key, label: measurement.label, unit: measurement.unit, values: [] };
        group.values.push({ date: meal.date, value: measurement.value });
        grouped.set(key, group);
      });
    });
    return [...grouped.values()];
  }, [meals]);

  const dateValidationMessage = useMemo(() => {
    if (!fromDate || !toDate) {
      return '시작일과 종료일을 모두 입력해 주세요.';
    }
    if (fromDate > toDate) {
      return '시작일은 종료일보다 늦을 수 없습니다.';
    }
    const diff = Math.floor((new Date(toDate).getTime() - new Date(fromDate).getTime()) / (1000 * 60 * 60 * 24)) + 1;
    if (diff > MAX_RANGE_DAYS) {
      return `조회 기간은 최대 ${MAX_RANGE_DAYS}일까지 가능합니다.`;
    }
    return null;
  }, [fromDate, toDate]);

  async function handleSearch() {
    setSearchLoading(true);
    setSearchError(null);
    setSelectedSchool(null);
    setMeals([]);
    setMealError(null);
    try {
      const response = await searchSchools(query);
      setSchools(response.items);
      setSearchMeta({ total: response.total, hasMore: response.hasMore });
    } catch (error) {
      setSchools([]);
      setSearchMeta(null);
      setSearchError(error as ApiError);
    } finally {
      setSearchLoading(false);
    }
  }

  async function handleMealLookup() {
    if (!selectedSchool || dateValidationMessage) {
      return;
    }
    setMealLoading(true);
    setMealError(null);
    try {
      const response = await fetchMeals({
        officeCode: selectedSchool.officeCode,
        schoolCode: selectedSchool.schoolCode,
        from: fromDate,
        to: toDate,
      });
      setMeals(response.items);
    } catch (error) {
      setMeals([]);
      setMealError(error as ApiError);
    } finally {
      setMealLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <section className={styles.hero}>
          <Text size={700} weight="semibold">급식 배틀</Text>
          <Text>학교를 검색하고 기간을 선택해 중식 메뉴와 영양 정보를 한 번에 확인하세요.</Text>
        </section>

        <div className={styles.grid}>
          <Card className={styles.card}>
            <Text className={styles.sectionTitle} weight="semibold">1. 학교 검색 및 선택</Text>
            <label className={styles.field}>
              <Text>학교명</Text>
              <div className={styles.searchRow}>
                <Input className={styles.input} value={query} onChange={(event) => setQuery((event.target as HTMLInputElement).value)} placeholder="예: 서울" aria-label="학교명 검색어" />
                <Button appearance="primary" onClick={handleSearch} disabled={searchLoading}>검색</Button>
              </div>
            </label>
            {searchLoading && <Spinner label="학교를 찾는 중입니다." />}
            {searchError && (
              <MessageBar intent="error">
                <MessageBarBody>{searchError.message}</MessageBarBody>
              </MessageBar>
            )}
            {!searchLoading && !searchError && searchMeta && schools.length === 0 && (
              <MessageBar>
                <MessageBarBody>일치하는 학교가 없습니다. 검색어를 더 구체적으로 입력해 주세요.</MessageBarBody>
              </MessageBar>
            )}
            <div className={styles.schoolList}>
              {schools.map((school) => (
                <Button
                  key={`${school.officeCode}-${school.schoolCode}`}
                  className={`${styles.schoolButton} ${selectedSchool?.schoolCode === school.schoolCode ? styles.selectedSchool : ''}`}
                  appearance={selectedSchool?.schoolCode === school.schoolCode ? 'primary' : 'secondary'}
                  onClick={() => {
                    setSelectedSchool(school);
                    setMeals([]);
                    setMealError(null);
                  }}
                >
                  <div>
                    <Text weight="semibold">{school.name}</Text>
                    <Text>{school.region} · {school.schoolType}</Text>
                  </div>
                </Button>
              ))}
            </div>
            {searchMeta?.hasMore && (
              <MessageBar>
                <MessageBarBody>검색 결과가 많습니다. 학교명을 더 구체적으로 입력해 주세요.</MessageBarBody>
              </MessageBar>
            )}
          </Card>

          <Card className={styles.card}>
            <Text className={styles.sectionTitle} weight="semibold">2. 날짜 범위 선택</Text>
            <Text>{selectedSchool ? `${selectedSchool.name} 선택됨` : '먼저 학교를 선택해 주세요.'}</Text>
            <div className={styles.dateGrid}>
              <label className={styles.field}>
                <Text>시작일</Text>
                <Input type="date" value={fromDate} onChange={(event) => setFromDate((event.target as HTMLInputElement).value)} aria-label="시작일" />
              </label>
              <label className={styles.field}>
                <Text>종료일</Text>
                <Input type="date" value={toDate} onChange={(event) => setToDate((event.target as HTMLInputElement).value)} aria-label="종료일" />
              </label>
              <Button appearance="primary" onClick={handleMealLookup} disabled={!selectedSchool || Boolean(dateValidationMessage) || mealLoading}>
                급식 조회
              </Button>
            </div>
            {dateValidationMessage && (
              <MessageBar intent="warning">
                <MessageBarBody>{dateValidationMessage}</MessageBarBody>
              </MessageBar>
            )}
            {mealError && (
              <MessageBar intent="error">
                <MessageBarBody>{mealError.message}</MessageBarBody>
              </MessageBar>
            )}
            {mealLoading && <Spinner label="중식 정보를 불러오는 중입니다." />}
          </Card>
        </div>

        <Card className={styles.card}>
          <Text className={styles.sectionTitle} weight="semibold">3. 날짜별 중식 결과</Text>
          {!mealLoading && meals.length === 0 && !mealError && (
            <Text>{selectedSchool ? '선택한 조건에 해당하는 중식 정보가 없습니다.' : '학교와 날짜를 선택한 뒤 중식 정보를 조회해 주세요.'}</Text>
          )}
          <div className={styles.resultList}>
            {meals.map((meal) => (
              <Card key={meal.date} className={styles.card}>
                <Text weight="semibold">{formatDate(meal.date)} · {meal.mealType}</Text>
                <ul className={styles.menuList}>
                  {meal.menu.map((item) => (
                    <li key={`${meal.date}-${item.name}`}>
                      {item.name}
                      {item.allergyCodes.length > 0 ? ` (${item.allergyCodes.join(', ')})` : ''}
                    </li>
                  ))}
                </ul>
                {meal.calories && <Text>열량: {meal.calories.sourceText}</Text>}
                {meal.nutritionText && <Text>영양 정보: {meal.nutritionText}</Text>}
                {meal.origin && <Text>원산지: {meal.origin}</Text>}
                <Text>알레르기 정보는 참고용이며, 섭취 전 학교 안내를 다시 확인해 주세요.</Text>
              </Card>
            ))}
          </div>
        </Card>

        {chartGroups.length > 0 && (
          <Card className={styles.card}>
            <Text className={styles.sectionTitle} weight="semibold">수치형 급식 정보 차트</Text>
            {chartGroups.map((group) => (
              <div key={group.key}>
                <Text weight="semibold">{group.label} ({group.unit})</Text>
                <div className={styles.chartWrap}>
                  <ResponsiveContainer>
                    <BarChart data={group.values}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis unit={group.unit} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" name={group.label} fill="#0f6cbd" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <Text>{group.values.map((value) => `${formatDate(value.date)}: ${value.value}${group.unit}`).join(' / ')}</Text>
              </div>
            ))}
          </Card>
        )}
      </div>
    </div>
  );
}
