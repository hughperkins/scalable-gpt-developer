import React, { useState } from 'react';
import TextInput from './TextInput.jsx';
import CompletionArea from './CompletionArea.jsx';
import FileManager from './FileManager.jsx';

function App() {
  const [prompt, setPrompt] = useState('');
  const [completion, setCompletion] = useState('');
  const [files, setFiles] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (prompt) {
      const response = await fetch('http://localhost:8080/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      const result = await response.json();
      setCompletion(result.completion);
      setFiles(result.files);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <TextInput value={prompt} setValue={setPrompt} />
        <button type='submit'>Submit</button>
      </form>
      <CompletionArea value={completion} />
      <FileManager files={files} />
    </div>
  );
}

export default App;