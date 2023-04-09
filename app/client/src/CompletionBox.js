import React from 'react';

const CompletionBox = ({ completion }) => {
  return (
    <textarea
      readOnly
      value={completion}
      style={{ width: '100%', height: '200px', resize: 'none' }}
    ></textarea>
  );
};

export default CompletionBox;
