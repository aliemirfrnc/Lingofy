'use client';

import { Card } from '@/components/app/Card';
import styles from './DashboardWidgets.module.css';

interface XPWidgetProps {
  xp: number;
  level: string;
}

export function XPWidget({ xp, level }: XPWidgetProps) {
  return (
    <Card className={styles.widgetCard}>
      <div className={styles.widgetHeader}>
        <svg className={styles.widgetIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
        <h3 className={styles.widgetTitle}>Experience</h3>
      </div>
      <div className={styles.widgetContent}>
        <div className={styles.largeValue}>{xp} XP</div>
        <div className={styles.subtext}>Current Level: {level}</div>
      </div>
    </Card>
  );
}
