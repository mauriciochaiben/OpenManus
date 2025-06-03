import React from 'react';

const TestComponent: React.FC = () => {
  return (
    <div
      style={{
        padding: '20px',
        backgroundColor: '#f0f0f0',
        textAlign: 'center',
        fontSize: '24px',
        color: '#333',
      }}
    >
      <h1>🎉 OpenManus Frontend is Working!</h1>
      <p>If you can see this, React is rendering correctly.</p>
    </div>
  );
};

export default TestComponent;
