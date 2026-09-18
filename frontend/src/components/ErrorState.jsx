import { AlertTriangle } from 'lucide-react';

export function ErrorState({ message }) {
  return (
    <div className="state-card error-state" role="alert">
      <AlertTriangle size={18} />
      <span>{message}</span>
    </div>
  );
}
