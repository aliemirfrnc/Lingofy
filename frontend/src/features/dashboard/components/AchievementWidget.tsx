'use client';

import { Card } from '@/components/app/Card';
import { cx } from '@/lib/app/utils';
import { Badge } from '../models/dashboardModels';
import styles from './DashboardWidgets.module.css';

interface AchievementWidgetProps {
  badges: Badge[];
}

export function AchievementWidget({ badges }: AchievementWidgetProps) {
  return (
    <Card className={styles.widgetCard}>
      <div className={styles.widgetHeader}>
        <svg className={styles.widgetIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 15l-2 5-9-5 5-9 9 5z" />
          <path d="M14 9l7-4-3 8-7 4-4-7z" />
        </svg>
        <h3 className={styles.widgetTitle}>Achievements</h3>
      </div>
      <div className={styles.badgeList}>
        {badges.map((badge) => (
          <div
            key={badge.id}
            className={cx(styles.badgeItem, badge.isUnlocked && styles.unlocked)}
            role="img"
            aria-label={`${badge.name} badge ${badge.isUnlocked ? 'unlocked' : 'locked'}`}
          >
            <span className={styles.badgeIcon} aria-hidden="true">{badge.icon}</span>
            <span className={styles.badgeName}>{badge.name}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
