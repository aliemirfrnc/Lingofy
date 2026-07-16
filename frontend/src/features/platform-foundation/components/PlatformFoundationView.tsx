import { Card } from '@/components/app/Card';
import { PlatformFoundationContext } from './PlatformFoundationContext';
import styles from './PlatformFoundationView.module.css';

export function PlatformFoundationView() {
  return (
    <main className={styles.main}>
      <Card className={styles.content} variant="outlined" padding="lg">
        <p className={styles.eyebrow}>Lingofy</p>
        <h1 className={styles.title}>Customer Platform</h1>
        <p className={styles.description}>
          Yeni müşteri platformu altyapısı etkin.
        </p>
        <PlatformFoundationContext />
      </Card>
    </main>
  );
}
