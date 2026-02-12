"use client";
import useSWR from "swr";
import { fetchApi, buildKey } from "@/lib/api";

export function useApi<T>(path: string, params?: Record<string, string | number | boolean>) {
  const key = buildKey(path, params);
  return useSWR<T>(key, () => fetchApi<T>(path, params), {
    revalidateOnFocus: false,
    dedupingInterval: 30000,
  });
}
