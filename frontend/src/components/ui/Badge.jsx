function Badge({
  children,
  className = "",
}) {
  return (
    <span
      className={`inline-block px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-medium ${className}`}
    >
      {children}
    </span>
  );
}

export default Badge;