// Test utilities for mocking and testing setup

// Mock WebSocket for testing
export class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  public readyState = MockWebSocket.CONNECTING;
  public onopen: ((event: Event) => void) | null = null;
  public onclose: ((event: CloseEvent) => void) | null = null;
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onerror: ((event: Event) => void) | null = null;

  private eventListeners: { [key: string]: ((event: any) => void)[] } = {};

  constructor(
    public url: string,
    public protocols?: string | string[],
  ) {
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event("open"));
    }, 0);
  }

  send(data: string | ArrayBufferLike | Blob | ArrayBufferView): void {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error("WebSocket is not open");
    }
    // Simulate message echo for testing
    setTimeout(() => {
      const event = new MessageEvent("message", { data });
      this.onmessage?.(event);
    }, 0);
  }

  close(code?: number, reason?: string): void {
    this.readyState = MockWebSocket.CLOSING;
    setTimeout(() => {
      this.readyState = MockWebSocket.CLOSED;
      const event = new CloseEvent("close", {
        code: code || 1000,
        reason: reason || "",
      });
      this.onclose?.(event);
    }, 0);
  }

  addEventListener(type: string, listener: (event: any) => void): void {
    if (!this.eventListeners[type]) {
      this.eventListeners[type] = [];
    }
    this.eventListeners[type].push(listener);
  }

  removeEventListener(type: string, listener: (event: any) => void): void {
    if (this.eventListeners[type]) {
      const index = this.eventListeners[type].indexOf(listener);
      if (index > -1) {
        this.eventListeners[type].splice(index, 1);
      }
    }
  }

  dispatchEvent(event: Event): boolean {
    const listeners = this.eventListeners[event.type] || [];
    listeners.forEach((listener) => listener(event));
    return true;
  }
}

// Mock fetch for API testing
export const mockFetch = jest.fn();

// Setup mock fetch globally
export const setupMockFetch = () => {
  global.fetch = mockFetch;
  return mockFetch;
};

// Helper to create mock API responses
export const mockApiResponse = (data: any, status = 200, ok = true) => {
  return Promise.resolve({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    headers: new Headers(),
    redirected: false,
    statusText: status === 200 ? "OK" : "Error",
    type: "default" as ResponseType,
    url: "",
    clone: jest.fn(),
    body: null,
    bodyUsed: false,
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
    blob: () => Promise.resolve(new Blob()),
    formData: () => Promise.resolve(new FormData()),
  });
};

// Mock localStorage
export const createMockLocalStorage = () => {
  const storage: { [key: string]: string } = {};

  const mockStorage = {
    getItem: jest.fn((key: string) => storage[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      storage[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete storage[key];
    }),
    clear: jest.fn(() => {
      Object.keys(storage).forEach((key) => delete storage[key]);
    }),
    key: jest.fn((index: number) => {
      const keys = Object.keys(storage);
      return keys[index] || null;
    }),
    get length() {
      return Object.keys(storage).length;
    },
  };

  Object.defineProperty(window, "localStorage", {
    value: mockStorage,
    writable: true,
  });

  return mockStorage;
};

// Mock sessionStorage
export const createMockSessionStorage = () => {
  const storage: { [key: string]: string } = {};

  const mockStorage = {
    getItem: jest.fn((key: string) => storage[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      storage[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete storage[key];
    }),
    clear: jest.fn(() => {
      Object.keys(storage).forEach((key) => delete storage[key]);
    }),
    key: jest.fn((index: number) => {
      const keys = Object.keys(storage);
      return keys[index] || null;
    }),
    get length() {
      return Object.keys(storage).length;
    },
  };

  Object.defineProperty(window, "sessionStorage", {
    value: mockStorage,
    writable: true,
  });

  return mockStorage;
};

// Setup test environment
export const setupTestEnvironment = () => {
  // Mock WebSocket
  global.WebSocket = MockWebSocket as any;

  // Mock fetch
  setupMockFetch();

  // Mock localStorage
  createMockLocalStorage();

  // Mock sessionStorage
  createMockSessionStorage();

  // Mock navigator.onLine
  Object.defineProperty(navigator, "onLine", {
    writable: true,
    value: true,
  });

  return {
    mockFetch,
    MockWebSocket,
    localStorage: window.localStorage,
    sessionStorage: window.sessionStorage,
  };
};

// Cleanup test environment
export const cleanupTestEnvironment = () => {
  jest.clearAllMocks();
  jest.resetAllMocks();
};

// Utility to wait for async operations
export const waitFor = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

// Utility to flush promises
export const flushPromises = () =>
  new Promise((resolve) => setImmediate(resolve));
