import React from 'react';

const TextInput = ({ value, setValue }) => {
  return (
    <div>
      <label htmlFor='userInput'>Prompt:</label>
      <textarea
        id='userInput'
        value={value}
        onChange={(e) => setValue(e.target.value)}
        rows={8}
        cols={60}
        style={{ resize: 'none' }}
      ></textarea>
    </div>
  );
};

export default TextInput;