import React, { useState } from 'react';

export const FileModal = ({ isOpen, content, filename, onRequestClose }) => {
  if (!isOpen) {
    return null;
  }

  const handleClose = () => {
    onRequestClose();
  };

  return (
    <div className='modal-overlay'>
      <div className='modal-content'>
        <h2>{filename}</h2>
        <pre className='file-content'>{content}</pre>
        <button onClick={handleClose}>Close</button>
      </div>
    </div>
  );
};