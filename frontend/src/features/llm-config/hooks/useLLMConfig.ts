/**
 * Custom hooks for LLM Configuration management
 */

import { useEffect } from "react";
import { useLLMConfigStore } from "../store/llmConfigStore";

// Hook to get and manage LLM providers
export const useLLMProviders = () => {
  const { providers, loading, error, fetchProviders, clearError } =
    useLLMConfigStore();

  useEffect(() => {
    if (providers.length === 0) {
      fetchProviders();
    }
  }, [providers.length, fetchProviders]);

  return {
    providers,
    loading,
    error,
    refetch: fetchProviders,
    clearError,
  };
};

// Hook to get and manage LLM configurations
export const useLLMConfigurations = () => {
  const {
    configurations,
    currentConfig,
    loading,
    error,
    fetchConfigurations,
    createConfiguration,
    updateConfiguration,
    deleteConfiguration,
    setDefaultConfiguration,
    toggleConfiguration,
    setCurrentConfig,
    clearError,
  } = useLLMConfigStore();

  useEffect(() => {
    fetchConfigurations();
  }, [fetchConfigurations]);

  return {
    configurations,
    currentConfig,
    loading,
    error,
    actions: {
      create: createConfiguration,
      update: updateConfiguration,
      delete: deleteConfiguration,
      setDefault: setDefaultConfiguration,
      toggle: toggleConfiguration,
      setCurrent: setCurrentConfig,
      refetch: fetchConfigurations,
      clearError,
    },
  };
};

// Hook for testing LLM configurations
export const useLLMTesting = () => {
  const { testResults, testConfiguration } = useLLMConfigStore();

  return {
    testResults,
    testConfiguration,
  };
};

// Hook for LLM usage statistics
export const useLLMUsageStats = () => {
  const { usageStats, fetchUsageStats } = useLLMConfigStore();

  return {
    usageStats,
    fetchUsageStats,
  };
};

// Hook to get the current active LLM configuration
export const useCurrentLLMConfig = () => {
  const currentConfig = useLLMConfigStore((state) => state.currentConfig);
  const setCurrentConfig = useLLMConfigStore((state) => state.setCurrentConfig);

  return {
    currentConfig,
    setCurrentConfig,
    isConfigured: !!currentConfig,
  };
};

// Hook to find provider by ID
export const useLLMProvider = (providerId: string) => {
  const providers = useLLMConfigStore((state) => state.providers);
  const provider = providers.find((p) => p.id === providerId);

  return provider;
};

// Hook to get configuration by ID
export const useLLMConfiguration = (configId: string | null) => {
  const configurations = useLLMConfigStore((state) => state.configurations);
  const configuration = configId
    ? configurations.find((c) => c.id === configId)
    : null;

  return configuration;
};
