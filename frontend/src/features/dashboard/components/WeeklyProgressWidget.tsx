'use client';

import { Card } from '@/components/app/Card';
import { HistoryRecord } from '../models/dashboardModels';
import styles from './DashboardWidgets.module.css';

interface WeeklyProgressWidgetProps {
  history: HistoryRecord[];
}

export function WeeklyProgressWidget({ history }: WeeklyProgressWidgetProps) {
  // If no history, show empty state or basic line
  const maxScore = Math.max(...history.map(h => h.score), 100);

  return (
    <Card className={styles.widgetCard}>
      <div className={styles.widgetHeader}>
        <svg className={styles.widgetIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
        <h3 className={styles.widgetTitle}>Recent Progress</h3>
      </div>
      <div className={styles.widgetContent}>
        <div className={styles.historyList} role="list" aria-label="Recent scores history">
          {history.length > 0 ? (
            history.map((record, index) => {
              const heightPercent = Math.max((record.score / maxScore) * 100, 5);
              return (
                <div key={index} className={styles.historyBarContainer} role="listitem">
                  <div
                    className={styles.historyBar}
                    style={{ height: `${heightPercent}%` }}
                    title={`${record.score} score on ${record.date}`}
                    aria-label={`${record.score} score on ${record.date}`}
                  />
                  <span className={styles.historyDate} aria-hidden="true">{record.date}</span>
                </div>
              );
            })
          ) : (
            <div className={styles.subtext}>No practice data yet.</div>
          )}
        </div>
      </div>
    </Card>
  );
}
