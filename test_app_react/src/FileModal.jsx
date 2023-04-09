import React, { useRef } from 'react';

const FileModal = ({ filename, content, close }) => {
  const contentRef = useRef();

  const handleCopyContent = () => {
    contentRef.current.select();
    document.execCommand('copy');
  };

  return (
    <div className='file-modal'>
      <div className='file-modal-content'>
        <h2>{filename}</h2>
        <textarea readOnly className='file-content' ref={contentRef} value={content} />
        <button onClick={handleCopyContent}>Copy Content</button>
        <button onClick={close}>Close</button>
      </div>
    </div>
  );
};

export default FileModal;
