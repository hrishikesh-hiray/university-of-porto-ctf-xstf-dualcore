import React from 'react';

function Element({ config }) {
  if (!config || typeof config !== 'object') {
    return null;
  }

  const { wrapper = 'div', children = [] } = config;

  const renderChildren = (childrenArray) => {
    if (!Array.isArray(childrenArray)) {
      return null;
    }

    return childrenArray.map((child, index) => {
      if (typeof child === 'string') {
        return child;
      } else if (typeof child === 'object') {
        return <Element key={index} config={child} />;
      }
      return null;
    });
  };

  return React.createElement(
    wrapper,
    null,
    ...renderChildren(children)
  );
}

export default Element;
