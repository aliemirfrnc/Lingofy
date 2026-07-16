'use client';

import { Card } from '@/components/app/Card';
import styles from './DashboardWidgets.module.css';

interface DailyGoalWidgetProps {
  goal: string;
}

export function DailyGoalWidget({ goal }: DailyGoalWidgetProps) {
  return (
    <Card className={styles.widgetCard}>
      <div className={styles.widgetHeader}>
        <svg className={styles.widgetIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 8v4l3 3" />
        </svg>
        <h3 className={styles.widgetTitle}>Daily Goal</h3>
      </div>
      <div className={styles.widgetContent}>
        <div className={styles.largeValue}>{goal}</div>
        <div className={styles.subtext}>Your focus for today</div>
      </div>
    </Card>
  );
}
