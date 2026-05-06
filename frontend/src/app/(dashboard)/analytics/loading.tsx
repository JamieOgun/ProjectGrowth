import { Skeleton } from "@/components/ui/skeleton";

function StatCardSkeleton() {
  return (
    <div className="flex-1 rounded-lg border border-neutral-200 bg-white px-5 py-4">
      <Skeleton className="mb-2 h-3 w-24" />
      <Skeleton className="mb-1 h-7 w-20" />
      <Skeleton className="h-3 w-16" />
    </div>
  );
}

function ChartPanelSkeleton() {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white px-5 py-4">
      <Skeleton className="mb-1 h-3 w-32" />
      <Skeleton className="mb-4 h-3 w-16" />
      <Skeleton className="h-[100px] w-full" />
    </div>
  );
}

function PostsTableSkeleton() {
  return (
    <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white">
      <div className="flex items-center justify-between border-b border-neutral-100 px-5 py-4">
        <Skeleton className="h-4 w-32" />
        <div className="flex gap-1.5">
          <Skeleton className="h-6 w-16 rounded-full" />
          <Skeleton className="h-6 w-20 rounded-full" />
          <Skeleton className="h-6 w-18 rounded-full" />
        </div>
      </div>
      <table className="w-full">
        <thead>
          <tr className="border-b border-neutral-100">
            {Array.from({ length: 7 }).map((_, i) => (
              <th key={i} className="px-4 py-2.5">
                <Skeleton className="h-2.5 w-12" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: 5 }).map((_, i) => (
            <tr key={i} className="border-b border-neutral-50 last:border-0">
              <td className="px-4 py-3">
                <Skeleton className="h-3 w-8" />
              </td>
              <td className="px-4 py-3">
                <Skeleton className="h-5 w-20" />
              </td>
              <td className="px-4 py-3">
                <Skeleton className="h-4 w-40" />
              </td>
              <td className="px-4 py-3">
                <Skeleton className="ml-auto h-4 w-14" />
              </td>
              <td className="px-4 py-3">
                <Skeleton className="ml-auto h-4 w-8" />
              </td>
              <td className="px-4 py-3">
                <Skeleton className="ml-auto h-4 w-8" />
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-1.5">
                  <Skeleton className="h-1.5 w-16 rounded-full" />
                  <Skeleton className="h-3 w-8" />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Loading() {
  return (
    <>
      {/* PageHeader skeleton */}
      <div className="mb-6">
        <Skeleton className="mb-1 h-3 w-56" />
        <div className="flex items-start justify-between gap-4">
          <Skeleton className="h-9 w-40" />
          <div className="flex gap-2">
            <Skeleton className="h-8 w-14" />
            <Skeleton className="h-8 w-24" />
          </div>
        </div>
        <div className="mt-4 border-b border-neutral-200" />
      </div>

      {/* Stat cards */}
      <div className="mb-6 flex gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>

      {/* Charts + Insight */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        <ChartPanelSkeleton />
        <ChartPanelSkeleton />
        <ChartPanelSkeleton />
      </div>

      {/* Posts table */}
      <PostsTableSkeleton />
    </>
  );
}
