import { useState, useEffect, useCallback } from 'react';
import { listSources } from '../services/knowledgeApi';
import type { KnowledgeSource, ApiError } from '../types/api';

interface UseKnowledgeSourcesReturn {
  sources: KnowledgeSource[];
  completedSources: KnowledgeSource[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  selectedSourceIds: string[];
  setSelectedSourceIds: (ids: string[]) => void;
  toggleSource: (sourceId: string) => void;
  clearSelection: () => void;
}

export const useKnowledgeSources = (): UseKnowledgeSourcesReturn => {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSourceIds, setSelectedSourceIds] = useState<string[]>([]);

  const fetchSources = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await listSources({ page_size: 100 }); // Get all sources
      setSources(response.sources);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message);
      console.error('Error fetching knowledge sources:', apiError);
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    await fetchSources();
  }, [fetchSources]);

  const toggleSource = useCallback((sourceId: string) => {
    setSelectedSourceIds((prev) =>
      prev.includes(sourceId)
        ? prev.filter((id) => id !== sourceId)
        : [...prev, sourceId]
    );
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedSourceIds([]);
  }, []);

  // Filter completed sources
  const completedSources = sources.filter(
    (source) => source.status.status === 'completed'
  );

  // Initial fetch
  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  return {
    sources,
    completedSources,
    loading,
    error,
    refresh,
    selectedSourceIds,
    setSelectedSourceIds,
    toggleSource,
    clearSelection,
  };
};
