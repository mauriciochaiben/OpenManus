// Canvas node components exports
import PromptNodeComponent from './PromptNode';
import ResponseNodeComponent from './ResponseNode';

export { PromptNodeComponent as PromptNode };
export { ResponseNodeComponent as ResponseNode };

// Node type registry for ReactFlow
export const nodeTypes = {
  promptNode: PromptNodeComponent,
  responseNode: ResponseNodeComponent,
};
