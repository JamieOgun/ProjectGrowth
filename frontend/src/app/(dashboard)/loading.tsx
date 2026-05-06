import { Skeleton } from "@/components/ui/skeleton";

function IdeaRowSkeleton() {
  return (
    <div className="flex w-full items-center gap-3 border-b border-neutral-100 px-4 py-3.5">
      <div className="w-0.5 flex-shrink-0 self-stretch rounded-full bg-neutral-200" />
      <div className="flex flex-shrink-0 items-center gap-1.5">
        <Skeleton className="h-5 w-20" />
        <Skeleton className="h-5 w-12" />
      </div>
      <Skeleton className="h-4 flex-1" />
      <Skeleton className="hidden h-3 w-20 sm:block" />
      <Skeleton className="h-3.5 w-3.5 flex-shrink-0" />
    </div>
  );
}

export default function Loading() {
  return (
    <>
      {/* PageHeader skeleton */}
      <div className="mb-6">
        <Skeleton className="mb-1 h-3 w-48" />
        <div className="flex items-start justify-between gap-4">
          <Skeleton className="h-9 w-36" />
          <div className="flex gap-2">
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-8 w-28" />
          </div>
        </div>
        <Skeleton className="mt-2 h-3 w-56" />
        <div className="mt-4 border-b border-neutral-200" />
      </div>

      {/* Idea list skeleton */}
      <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white">
        {Array.from({ length: 8 }).map((_, i) => (
          <IdeaRowSkeleton key={i} />
        ))}
      </div>
    </>
  );
}
