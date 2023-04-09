import React from 'react';
import './App.css';
import Modal from 'react-modal';

Modal.setAppElement('#root');

export default function FileModal({ isOpen, content, onRequestClose }) {
  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      className='FileModal'
      overlayClassName='Overlay'
    >
      <pre>{content}</pre>
      <button onClick={onRequestClose}>Close</button>
    </Modal>
  );
}
