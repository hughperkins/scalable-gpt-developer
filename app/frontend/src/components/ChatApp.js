import React, { useState } from 'react';
import axios from 'axios';
import FileModal from './FileModal';

const ChatApp = () => {
  const [inputPrompt, setInputPrompt] = useState('');
  const [outputCompletion, setOutputCompletion] = useState('');
  const [fileList, setFileList] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const handleInputChange = (event) => {
    setInputPrompt(event.target.value);
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post('/chat', { prompt: inputPrompt });
      const completion = response.data.completion;
      const parsedCompletion = parseCompletion(completion);
      setOutputCompletion(parsedCompletion.text);
      setFileList(parsedCompletion.files);
    } catch (error) {
      console.error('Error fetching completion:', error);
    }
  };

  const handleFileClick = (file) => {
    setSelectedFile(file);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
  };

  const parseCompletion = (completion) => {
    const regex = /^([\w.]+)\.?(?:.*)?\\n^```([^]*)```/gm;
    const files = [];
    let match;

    while ((match = regex.exec(completion)) !== null) {
      files.push({ name: match[1], content: match[2] });
    }

    const text = completion.replace(regex, '').trim();

    return { text, files };
  };

  return (
    <div>
      <textarea
        value={inputPrompt}
        onChange={handleInputChange}
        placeholder='Enter your prompt...'
        rows={6}
        style={{ width: '100%', marginBottom: '1rem' }}
      />
      <button onClick={handleSubmit}>Submit</button>

      <div style={{ marginTop: '1rem', maxHeight: '200px', overflow: 'auto' }}>
        {fileList.map((file) => (
          <div key={file.name} onClick={() => handleFileClick(file)}>
            {file.name}
          </div>
        ))}
      </div>

      <textarea
        value={outputCompletion}
        readOnly
        rows={6}
        style={{ width: '100%', marginTop: '1rem', backgroundColor: '#f5f5f5' }}
      />

      {modalOpen && (
        <FileModal
          open={modalOpen}
          file={selectedFile}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default ChatApp;