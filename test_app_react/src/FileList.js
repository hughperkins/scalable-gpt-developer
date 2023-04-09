import React, { useState } from 'react';
import FileModal from './FileModal.js';

const FileList = ({ files }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const openModal = (content) => {
    setSelectedFile(content);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
  };

  return (
    <div>
      <ul>
        {Object.keys(files).map((fileName) => (
          <li key={fileName} onClick={() => openModal(files[fileName])}>
            {fileName}
          </li>
        ))}
      </ul>
      <FileModal
        isOpen={modalOpen}
        content={selectedFile}
        onRequestClose={closeModal}
      />
    </div>
  );
};

export default FileList;
