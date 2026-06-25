export default function ErrorBanner({ message, onRetry }) {
  return (
    <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 text-center mb-5">
      <p className="text-red-400 text-sm m-0 mb-2">{message}</p>
      {onRetry && (
        <button 
          onClick={onRetry} 
          className="px-4 py-1.5 rounded-lg border-none bg-red-500/20 hover:bg-red-500/30 text-red-400 text-sm font-medium cursor-pointer transition-colors"
        >
          Tekrar dene
        </button>
      )}
    </div>
  );
}
