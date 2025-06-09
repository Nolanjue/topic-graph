import React, { useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import axios from 'axios';

// Randomize node positions
const getRandomPosition = () => ({
  x: Math.random() * 800 + 100,
  y: Math.random() * 400 + 100
});


const initialElements: any = [];

const layout = { name: "preset" };

const style = [
  // Default node styling
  //added styles for every appended new topics to differentiate it!
  {
    selector: "node",
    style: {
      label: "data(label)",
      color: "#ffffff",
      "font-size": "25px",
      "font-weight": "700",
      "font-family": "Inter, system-ui, sans-serif",
      "background-gradient-direction": "to-bottom-right",
      "background-gradient-stop-colors": "#6366f1 #8b5cf6",
      "background-fill": "linear-gradient",
      width: 120,
      height: 120,
      "shape": "ellipse",
      "border-width": 3,
      "border-color": "#ec4899",
      "border-opacity": 1,
      "text-outline-color": "#000000",
      "text-outline-width": 2,
      "text-outline-opacity": 0.8,
      "shadow-blur": 25,
      "shadow-color": "#6366f1",
      "shadow-opacity": 0.7,
      "shadow-offset-x": 0,
      "shadow-offset-y": 6,
      "text-wrap": "wrap",
      "text-max-width": "100px",
    
    },
  },

  // Parent topic styling
  {
    selector: ":parent",
    style: {
      "background-opacity": 0.2,
      "background-color": "#8b5cf6",
      "border-color": "#8b5cf6",
      "border-width": 4,
      "border-style": "solid",
      "border-opacity": 0.8,
      "shape": "round-rectangle",
      padding: "50px",
      "font-size": "40px",
      "font-weight": "700",
      color: "#e879f9",
      "text-outline-color": "#000000",
      "text-outline-width": 2,
      "text-outline-opacity": 0.7,
      "shadow-blur": 30,
      "shadow-color": "#a78bfa",
      "shadow-opacity": 0.5,
      "shadow-offset-x": 0,
      "shadow-offset-y": 8,
      "background-gradient-stop-colors": "#E74C3C #F39C12",
    
    },
  },

  // Hover effects
  {
    selector: "node:hover",
    style: {
      "border-width": 4,
      "shadow-blur": 35,
      "shadow-opacity": 0.9,
      transform: "scale(1.1)",
      "transition-duration": "0.3s",
    },
  },

  // Edge styling
  {
    selector: "edge",
    style: {
      label: "data(label)",
      width: 3,
      "line-color": "#a855f7",
      "target-arrow-color": "#ec4899",
      "target-arrow-shape": "triangle",
      "target-arrow-size": 12,
      "curve-style": "bezier",
      "font-size": "20px",
      "font-weight": "600",
      color: "#fbbf24",
      "text-background-color": "#1e293b",
      "text-background-opacity": 0.9,
      "text-background-padding": "4px",
      "text-background-shape": "round-rectangle",
      "text-border-color": "#a855f7",
      "text-border-width": 1,
      "text-border-opacity": 0.8,
      opacity: 0.8,
      "font-family": "Inter, system-ui, sans-serif",
    },
  },

  {
    selector: "edge:hover",
    style: {
      width: 5,
      "line-color": "#06b6d4",
      "target-arrow-color": "#3b82f6",
      opacity: 1,
      "transition-duration": "0.3s",
    },
  },
];

function App() {
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);

  // State arrays for Flask integration
  const [elements, setElements] = useState(initialElements);
  const [styles, setStyles] = useState(style);
  const [topics, setTopics] = useState([]);
  const [chunks, setChunks] = useState([]);
  const [similarities, setSimilarities] = useState([]);

  // PDF upload states
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  // Handle PDF file upload
  const handleFileUpload = (event: any) => {
    const files = Array.from(event.target.files);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');

    if (pdfFiles.length !== files.length) {
      setUploadStatus("Only PDF files are allowed!");
      setTimeout(() => setUploadStatus(""), 3000);
      return;
    }

    setUploadedFiles(prev => [...prev, ...pdfFiles]);
    setUploadStatus(`${pdfFiles.length} PDF file(s) added successfully!`);
    setTimeout(() => setUploadStatus(""), 3000);
  };

  // Remove uploaded file
  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Submit data to Flask backend
  const submitToFlask = async () => {
    if (uploadedFiles.length === 0) {
      setUploadStatus("Please upload at least one PDF file!");
      setTimeout(() => setUploadStatus(""), 3000);
      return;
    }

    setIsUploading(true);
    setUploadStatus("Processing PDFs and generating graph...");

    try {
      const formData = new FormData();

      // Add PDF files
      uploadedFiles.forEach((file, index) => {
        formData.append(`pdf_${index}`, file);
      });

      // Add JSON data
      const jsonData = {
        styles: styles,
        elements: elements,
        topics: topics,
        chunks: chunks,
        similarities: similarities
      };

      formData.append('data', JSON.stringify(jsonData));

      const response = await axios.post('http://127.0.0.1:5000/submit', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, //30 second timeout for large file uploads and processing
      });
      if (response.data) {
        const result = await response.data;
      
        // Update state with results from Flask
        if (result.elements) {
          setElements(result.elements);
        }
        if (result.styles) {
          setStyles(result.styles);
        }
        if (result.topics) {
          setTopics(result.topics);
        }
        if (result.chunks) {
          setChunks(result.chunks);
        }
        if (result.similarities) {
          setSimilarities(result.similarities);
        }

        setUploadStatus("Graph updated successfully!");
        setUploadedFiles([]); 
      } else {
        const errorResult = await response.data;
        throw new Error(errorResult.error || 'Failed to process PDFs');
      }
    } catch (error) {
      console.error('Error:', error);
      setUploadStatus(`Error: ${error.message}`);
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadStatus(""), 5000);
    }
  };

  // Reset all states
  const resetStates = () => {
    setElements([]);
    setStyles(style);
    setTopics([]);
    setChunks([]);
    setSimilarities([]);
    setUploadedFiles([]);
    setSelectedNode(null);
    setSelectedEdge(null);
    setUploadStatus("Graph reset successfully!");
    setTimeout(() => setUploadStatus(""), 2000);
  };

  // Center the graph
  const centerGraph = () => {
 //TODO: not necessary, but can do later
    setUploadStatus("Graph centered!");
    setTimeout(() => setUploadStatus(""), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="text-center py-8">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent mb-4">
          Topic Similarity Graph
        </h1>
        <p className="text-slate-300 text-xl">Interactive visualization of text and topic relationships within PDFs </p>
      </div>

      {/* Main Layout */}
      <div className="flex gap-6 px-6 pb-8">
        {/* Left Panel */}
        <div className="w-80 flex-shrink-0">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 mb-6">
            <h2 className="text-xl font-bold text-purple-300 mb-4 flex items-center">
              <span className="w-3 h-3 bg-purple-500 rounded-full mr-3"></span>
              Graph Controls
            </h2>
            <div className="space-y-4">
              <button
                onClick={resetStates}
                className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-200 shadow-lg"
              >
                Reset Graph
              </button>
              <button
                onClick={centerGraph}
                className="w-full px-4 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg font-semibold hover:from-cyan-700 hover:to-blue-700 transition-all duration-200 shadow-lg"
              >
                Center Graph
              </button>
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
            <h2 className="text-xl font-bold text-cyan-300 mb-4 flex items-center">
              <span className="w-3 h-3 bg-cyan-500 rounded-full mr-3"></span>
              Node Details
            </h2>
            {selectedNode ? (
              <div className="space-y-3">
                <div className="p-3 bg-slate-700/50 rounded-lg">
                  <p className="text-slate-300 text-sm">Label</p>
                  <p className="text-white font-semibold">
                    {elements.find(el => el.data?.id === selectedNode)?.data?.label || 'N/A'}
                  </p>
                </div>
                <div className="p-3 bg-slate-700/50 rounded-lg">
                  <p className="text-slate-300 text-sm">ID</p>
                  <p className="text-white font-semibold">{selectedNode}</p>
                </div>
                <div className="p-3 bg-slate-700/50 rounded-lg">
                  <p className="text-slate-300 text-sm">Text Chunk</p>
                  <div className="text-white text-sm max-h-32 overflow-y-auto bg-slate-800/50 rounded p-2 mt-2">
                    {elements.find(el => el.data?.id === selectedNode)?.data?.chunk || 'No text chunk available for this node.'}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-slate-400 italic">Click a node to see details</p>
            )}
          </div>
        </div>

        {/* Center - Graph */}
        <div className="flex-1 flex justify-center">
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-2xl overflow-hidden">
            <CytoscapeComponent
              elements={elements}
              layout={layout}
              style={{
                width: "900px",
                height: "700px",
                background: "radial-gradient(ellipse at center, #1e293b 0%, #0f172a 100%)",
              }}
              stylesheet={styles}
              cy={(cy) => {
                cy.on('tap', 'node', function (evt) {
                  const node = evt.target;
                  setSelectedNode(node.id());
                  console.log('Tapped node:', node.id());
                });

                cy.on('tap', 'edge', function (evt) {
                  const edge = evt.target;
                  setSelectedEdge({
                    id: edge.id(),
                    source: edge.source().id(),
                    target: edge.target().id(),
                    weight: edge.data('label')
                  });
                  console.log('Tapped edge:', edge.id(), 'weight:', edge.data('label'));
                });
              }}
            />
          </div>
        </div>

        {/* Right Panel */}
        <div className="w-80 flex-shrink-0">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 mb-6">
            <h2 className="text-xl font-bold text-pink-300 mb-4 flex items-center">
              <span className="w-3 h-3 bg-pink-500 rounded-full mr-3"></span>
              Edge Details
            </h2>
            {selectedEdge ? (
              <div className="space-y-3">
                <div className="p-3 bg-slate-700/50 rounded-lg">
                  <p className="text-slate-300 text-sm">Connection</p>
                  <p className="text-white font-semibold">{selectedEdge.source} → {selectedEdge.target}</p>
                </div>
                <div className="p-3 bg-slate-700/50 rounded-lg">
                  <p className="text-slate-300 text-sm">Similarity Score</p>
                  <p className="text-white font-semibold text-2xl">{selectedEdge.weight}</p>
                </div>
              </div>
            ) : (
              <p className="text-slate-400 italic">Click an edge to see details</p>
            )}
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
            <h2 className="text-xl font-bold text-emerald-300 mb-4 flex items-center">
              <span className="w-3 h-3 bg-emerald-500 rounded-full mr-3"></span>
              PDF Upload
            </h2>

            {/* File Upload Input */}
            <div className="mb-4">
              <label className="block w-full">
                <div className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center hover:border-emerald-500 transition-colors cursor-pointer">
                  <svg className="mx-auto h-12 w-12 text-slate-400 mb-2" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <p className="text-slate-300">Click to upload PDFs</p>
                  <p className="text-slate-500 text-sm">or drag and drop</p>
                </div>
                <input
                  type="file"
                  multiple
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="mb-4 max-h-32 overflow-y-auto">
                <h3 className="text-sm font-semibold text-slate-300 mb-2">Uploaded Files:</h3>
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-slate-700/50 rounded p-2 mb-1">
                    <span className="text-xs text-slate-300 truncate">{file.name}</span>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-400 hover:text-red-300 ml-2"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Submit Button */}
            <button
              onClick={submitToFlask}
              disabled={isUploading || uploadedFiles.length === 0}
              className={`w-full px-4 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg ${isUploading || uploadedFiles.length === 0
                ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:from-emerald-700 hover:to-teal-700'
                }`}
            >
              {isUploading ? 'Processing...' : 'Generate Graph'}
            </button>

            {/* Status Message */}
            {uploadStatus && (
              <div className={`mt-3 p-2 rounded text-sm ${uploadStatus.includes('Error') || uploadStatus.includes('Please upload')
                ? 'bg-red-900/50 text-red-300 border border-red-700'
                : 'bg-green-900/50 text-green-300 border border-green-700'
                }`}>
                {uploadStatus}
              </div>
            )}

            {/* Debug Info */}
            <div className="mt-4 p-3 bg-slate-700/30 rounded-lg">
              <h3 className="text-xs font-semibold text-slate-400 mb-2">Debug Info:</h3>
              <div className="text-xs text-slate-500 space-y-1">
                <div>Topics: {topics.length}</div>
                <div>Elements: {elements.length}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;