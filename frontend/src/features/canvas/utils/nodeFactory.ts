/**
 * Node Factory Utilities
 * Helper functions to create different types of nodes
 */

import { CanvasNode } from "../types";

export const createPromptNode = (
  position: { x: number; y: number },
  overrides: Partial<CanvasNode["data"]> = {},
): CanvasNode => {
  const id = `prompt-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  return {
    id,
    type: "promptNode",
    position,
    data: {
      label: "Prompt",
      prompt: "",
      description: "AI prompt node for text generation",
      status: "idle",
      ...overrides,
    },
  };
};

export const createNodeFromTemplate = (
  template: {
    type: string;
    label: string;
    description: string;
    defaultData: Record<string, any>;
  },
  position: { x: number; y: number },
): CanvasNode => {
  const id = `${template.type}-${Date.now()}-${Math.random()
    .toString(36)
    .substr(2, 9)}`;

  return {
    id,
    type: template.type,
    position,
    data: {
      label: template.label,
      description: template.description,
      status: "idle",
      ...template.defaultData,
    },
  };
};

export const createResponseNode = (
  position: { x: number; y: number },
  overrides: Partial<CanvasNode["data"]> = {},
): CanvasNode => {
  const id = `response-${Date.now()}-${Math.random()
    .toString(36)
    .substr(2, 9)}`;

  return {
    id,
    type: "responseNode",
    position,
    data: {
      label: "Response",
      response: "",
      description: "AI response output node",
      status: "idle",
      ...overrides,
    },
  };
};

// Default node templates
export const DEFAULT_NODE_TEMPLATES = [
  {
    id: "prompt",
    type: "promptNode",
    label: "Prompt",
    description: "AI prompt node for text generation",
    category: "AI",
    icon: "message",
    defaultData: {
      prompt: "",
      editable: true,
      placeholder: "Enter your prompt here...",
    },
  },
  {
    id: "response",
    type: "responseNode",
    label: "Response",
    description: "AI response output node",
    category: "AI",
    icon: "output",
    defaultData: {
      response: "",
      status: "idle",
    },
  },
];
