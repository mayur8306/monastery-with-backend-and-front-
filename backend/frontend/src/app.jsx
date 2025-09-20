import MonasteryList from './components/monasterylist';
import PanoramaViewer from './components/panoramaviewer';
import { useState } from 'react';

export default function App() {
  // Set a sample panorama URL for testing (update after uploads)
  const [panoramaUrl, setPanoramaUrl] = useState("http://127.0.0.1:8000/media/panoramas/sample.jpg");

  return (
    <div style={{ padding: 20 }}>
      <h1>Monastery360 Test Client</h1>
      <MonasteryList />
      <PanoramaViewer imageUrl={panoramaUrl} />
    </div>
  );
}
