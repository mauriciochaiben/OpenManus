/**
 * LLM Configuration Store using Zustand
 */

import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import {
  LLMConfiguration,
  LLMProvider,
  LLMTestResult,
  LLMUsageStats,
} from "../types";
import { llmConfigService } from "../services/llmConfigApi";

interface LLMConfigState {
  // State
  providers: LLMProvider[];
  configurations: LLMConfiguration[];
  currentConfig: LLMConfiguration | null;
  loading: boolean;
  error: string | null;
  testResults: Record<string, LLMTestResult>;
  usageStats: Record<string, LLMUsageStats>;

  // Actions
  fetchProviders: () => Promise<void>;
  fetchConfigurations: () => Promise<void>;
  createConfiguration: (config: any) => Promise<LLMConfiguration>;
  updateConfiguration: (id: string, updates: any) => Promise<LLMConfiguration>;
  deleteConfiguration: (id: string) => Promise<void>;
  setDefaultConfiguration: (id: string) => Promise<void>;
  testConfiguration: (id: string, testRequest?: any) => Promise<LLMTestResult>;
  toggleConfiguration: (id: string, isActive: boolean) => Promise<void>;
  fetchUsageStats: (id: string) => Promise<void>;
  setCurrentConfig: (config: LLMConfiguration | null) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  providers: [],
  configurations: [],
  currentConfig: null,
  loading: false,
  error: null,
  testResults: {},
  usageStats: {},
};

export const useLLMConfigStore = create<LLMConfigState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        fetchProviders: async () => {
          set({ loading: true, error: null });
          try {
            const providers = await llmConfigService.getProviders();
            set({ providers, loading: false });
          } catch (error) {
            set({
              error:
                error instanceof Error
                  ? error.message
                  : "Failed to fetch providers",
              loading: false,
            });
          }
        },

        fetchConfigurations: async () => {
          set({ loading: true, error: null });
          try {
            const response = await llmConfigService.getConfigurations();
            const configurations = response.configurations;

            // Set current config to default if none is set
            const currentConfig = get().currentConfig;
            if (!currentConfig) {
              const defaultConfig =
                configurations.find((c) => c.isDefault) || configurations[0];
              set({
                configurations,
                currentConfig: defaultConfig,
                loading: false,
              });
            } else {
              set({ configurations, loading: false });
            }
          } catch (error) {
            set({
              error:
                error instanceof Error
                  ? error.message
                  : "Failed to fetch configurations",
              loading: false,
            });
          }
        },

        createConfiguration: async (config) => {
          set({ loading: true, error: null });
          try {
            const newConfig =
              await llmConfigService.createConfiguration(config);
            const configurations = [...get().configurations, newConfig];

            // If this is the first config or marked as default, set it as current
            const shouldSetAsCurrent =
              configurations.length === 1 || newConfig.isDefault;

            set({
              configurations,
              currentConfig: shouldSetAsCurrent
                ? newConfig
                : get().currentConfig,
              loading: false,
            });

            return newConfig;
          } catch (error) {
            set({
              error:
                error instanceof Error
                  ? error.message
                  : "Failed to create configuration",
              loading: false,
            });
            throw error;
          }
        },

        updateConfiguration: async (id, updates) => {
          set({ loading: true, error: null });
          try {
            const updatedConfig = await llmConfigService.updateConfiguration(
              id,
              updates,
            );
            const configurations = get().configurations.map((c) =>
              c.id === id ? updatedConfig : c,
            );

            // Update current config if it's the one being updated
            const currentConfig = get().currentConfig;
            const newCurrentConfig =
              currentConfig?.id === id ? updatedConfig : currentConfig;

            set({
              configurations,
              currentConfig: newCurrentConfig,
              loading: false,
            });

            return updatedConfig;
          } catch (error) {
            set({
              error:
                error instanceof Error
                  ? error.message
                  : "Failed to update configuration",
              loading: false,
            });
            throw error;
          }
        },

        deleteConfiguration: async (id) => {
          set({ loading: true, error: null });
          try {
            await llmConfigService.deleteConfiguration(id);
            const configurations = get().configurations.filter(
              (c) => c.id !== id,
            );

            // If deleted config was current, set new default
            const currentConfig = get().currentConfig;
            let newCurrentConfig =
              currentConfig?.id === id ? null : currentConfig;

            if (!newCurrentConfig && configurations.length > 0) {
              newCurrentConfig =
                configurations.find((c) => c.isDefault) || configurations[0];
            }

            set({
              configurations,
              currentConfig: newCurrentConfig,
              loading: false,
            });
          } catch (error) {
            set({
              error:
                error instanceof Error
                  ? error.message
                  : "Failed to delete configuration",
              loading: false,
            });
            throw error;
          }
        },

        setDefaultConfiguration: async (id) => {
          set({ loading: true, error: null });
          try {
            const updatedConfig =
              await llmConfigService.setDefaultConfiguration(id);

            // Update all configurations to remove default from others
            const configurations = get().configurations.map((c) => ({
              ...c,
              isDefault: c.id === id,
            }));

            set({
              configurations,
              currentConfig: updatedConfig,
              loading: false,
            });
          } catch (error) {
            set({
              error:
                error instanceof Error
                  ? error.message
                  : "Failed to set default configuration",
              loading: false,
            });
            throw error;
          }
        },

        testConfiguration: async (id, testRequest) => {
          try {
            const result = await llmConfigService.testConfiguration(
              id,
              testRequest,
            );
            const testResults = { ...get().testResults, [id]: result };
            set({ testResults });
            return result;
          } catch (error) {
            const failedResult: LLMTestResult = {
              success: false,
              latency: 0,
              error: error instanceof Error ? error.message : "Test failed",
              timestamp: new Date().toISOString(),
            };
            const testResults = { ...get().testResults, [id]: failedResult };
            set({ testResults });
            throw error;
          }
        },

        toggleConfiguration: async (id, isActive) => {
          await get().updateConfiguration(id, { isActive });
        },

        fetchUsageStats: async (id) => {
          try {
            const stats = await llmConfigService.getUsageStats(id);
            const usageStats = { ...get().usageStats, [id]: stats };
            set({ usageStats });
          } catch (error) {
            console.error("Failed to fetch usage stats:", error);
          }
        },

        setCurrentConfig: (config) => {
          set({ currentConfig: config });
        },

        clearError: () => {
          set({ error: null });
        },

        reset: () => {
          set(initialState);
        },
      }),
      {
        name: "llm-config-store",
        partialize: (state) => ({
          currentConfig: state.currentConfig,
          configurations: state.configurations,
          providers: state.providers,
        }),
      },
    ),
    {
      name: "llm-config-store",
    },
  ),
);
