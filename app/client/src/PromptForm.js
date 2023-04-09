import React, { useState } from 'react';

const PromptForm = ({ onSubmit }) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(prompt);
  };

  const handleChange = (e) => {
    setPrompt(e.target.value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="prompt">Enter your prompt:</label>
      <br/>
      <textarea
        id="prompt"
        value={prompt}
        onChange={handleChange}
        rows={10}
        cols={50}
      />
      <br/>
      <button type="submit">Submit</button>
    </form>
  );
}

export default PromptForm;
