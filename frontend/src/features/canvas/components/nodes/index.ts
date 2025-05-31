// Canvas node components exports

export { default as PromptNode } from './PromptNode';
export { default as ResponseNode } from './ResponseNode';

// Node type registry for ReactFlow
export const nodeTypes = {
    promptNode: PromptNode,
    responseNode: ResponseNode,
};
