const WidgetWrapper = ({ children, className = "" }) => {
    return (
      <div className={`
        p-6 pb-3
        bg-white dark:bg-slate-800
        rounded-2xl
        shadow-lg hover:shadow-xl
        transition-all duration-300
        border border-slate-200/50 dark:border-slate-700/50
        backdrop-blur-sm
        ${className}
      `}>
        {children}
      </div>
    );
  };
  
  export default WidgetWrapper;