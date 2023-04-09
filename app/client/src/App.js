import React, { useState } from 'react';
import axios from 'axios';
import FileList from './FileList';
import PromptForm from './PromptForm';
import CompletionBox from './CompletionBox';
import './App.css';

function App() {
  const [completion, setCompletion] = useState('');
  const [files, setFiles] = useState({});

  const handleSubmit = async (prompt) => {
    try {
      const response = await axios.post('http://localhost:8080/chat', { prompt });
      const { content, extractedFiles } = response.data;
      setCompletion(content);
      setFiles(extractedFiles);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className='App'>
      <header className='App-header'>
        <h1>OpenAI Chat Completion</h1>
      </header>
      <main className='App-main'>
        <PromptForm onSubmit={handleSubmit} />
        <CompletionBox completion={completion} />
        <FileList files={files} />
      </main>
    </div>
  );
}

export default App;
