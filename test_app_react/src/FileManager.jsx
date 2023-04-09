import React from 'react';
import FileModal from './FileModal.jsx';

const FileManager = ({ files }) => {
  const [openModal, setOpenModal] = React.useState(false);
  const [selectedFile, setSelectedFile] = React.useState(null);

  const openFile = (filename) => {
    setSelectedFile(filename);
    setOpenModal(true);
  };

  const closeModal = () => {
    setOpenModal(false);
    setSelectedFile(null);
  };

  return (
    <div className='file-manager'>
      <h3>Files</h3>
      <ul className='file-list'>
        {Object.keys(files).map((filename, index) => (
          <li key={index} onClick={() => openFile(filename)}>{filename}</li>
        ))}
      </ul>
      {openModal && selectedFile && (
        <FileModal
          filename={selectedFile}
          content={files[selectedFile]}
          close={closeModal}
        />
      )}
    </div>
  );
};

export default FileManager;
