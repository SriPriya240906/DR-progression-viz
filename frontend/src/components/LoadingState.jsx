import { LoaderCircle } from 'lucide-react';

export function LoadingState({ message = 'Loading analysis...' }) {
  return (
    <div className="state-card loading-state" role="status" aria-live="polite">
      <LoaderCircle size={18} className="spin" />
      <span>{message}</span>
    </div>
  );
}
