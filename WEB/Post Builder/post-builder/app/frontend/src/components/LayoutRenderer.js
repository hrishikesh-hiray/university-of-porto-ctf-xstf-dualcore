import React from 'react';
import Element from './Element';

function LayoutRenderer({ layout }) {
  if (!Array.isArray(layout)) {
    return <div>Invalid layout</div>;
  }

  return (
    <div className="layout-container">
      {layout.map((element, index) => (
        <Element key={index} config={element} />
      ))}
    </div>
  );
}

export default LayoutRenderer;
