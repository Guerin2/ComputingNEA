import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import Router from "./Router";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Router/>
  </React.StrictMode>,
  document.getElementById("root")
);