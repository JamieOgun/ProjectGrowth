import { cn } from "@/lib/utils";

interface PageHeaderProps {
  breadcrumb: string;
  title: string;
  actions?: React.ReactNode;
  subtitle?: string;
  className?: string;
}

export function PageHeader({
  breadcrumb,
  title,
  actions,
  subtitle,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn("mb-6", className)}>
      <p className="mb-1 font-mono text-xs text-neutral-400">{breadcrumb}</p>
      <div className="flex items-start justify-between gap-4">
        <h1 className="text-3xl leading-tight font-bold tracking-tight">
          {title}
        </h1>
        {actions && (
          <div className="flex flex-shrink-0 items-center gap-2">{actions}</div>
        )}
      </div>
      {subtitle && (
        <p className="mt-1.5 font-mono text-xs text-neutral-400">{subtitle}</p>
      )}
      <div className="mt-4 border-b border-neutral-200" />
    </div>
  );
}
