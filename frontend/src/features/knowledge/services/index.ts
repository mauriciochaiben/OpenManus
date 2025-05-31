// Knowledge feature services exports
// This file will export all knowledge-related service classes and functions

export * from './knowledgeApi';

// Export utility functions for external use
export { useKnowledgeSources } from '../hooks/useKnowledgeSources';

// Add helper function for retry processing
export const retrySourceProcessing = async (sourceId: string) => {
    // Implementation would go in knowledgeApi.ts
    return await retryProcessing(sourceId);
};
