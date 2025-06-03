// Knowledge feature services exports
// This file will export all knowledge-related service classes and functions

export * from "./knowledgeApi";

// Export utility functions for external use
export { useKnowledgeSources } from "../hooks/useKnowledgeSources";

// Export the reprocessSource directly and also provide the compatibility function
export { reprocessSource } from "./knowledgeApi";

// Add back the helper function for compatibility with existing tests
export const retrySourceProcessing = async (sourceId: string) => {
  const { reprocessSource } = await import("./knowledgeApi");
  return await reprocessSource(sourceId);
};
