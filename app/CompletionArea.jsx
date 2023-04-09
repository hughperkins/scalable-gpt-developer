import React from 'react';

const CompletionArea = ({ value }) => {
  return (
    <div className='completion-area'>
      <textarea
        value={value}
        readOnly
        rows={10}
        cols={50}
        className='completion-textarea'
      />
    </div>
  );
};

export default CompletionArea;