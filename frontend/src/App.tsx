import React, { useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";


// Randomize node positions
const getRandomPosition = () => ({
  x: Math.random() * 800 + 100,
  y: Math.random() * 400 + 100
});

// Add compound node (cluster) with randomized positions
const elements = [
  // Cluster/parent node (for styling only)
  { data: { id: "cluster1", label: "Eyes", } },

  // Children nodes in cluster1 with randomized positions
  { data: { id: "a", label: "Node A", parent: "cluster1" }, position: getRandomPosition() },
  { data: { id: "b", label: "Node B", parent: "cluster1" }, position: getRandomPosition() },
  
  // Node outside any cluster with randomized position
  { data: { id: "c", label: "Node C" }, position: getRandomPosition() },

  // Edges with larger labels
  { data: { id: "ab", source: "a", target: "b", label: "0.85" } },
  { data: { id: "ac", source: "a", target: "c", label: "0.72" } },
  { data: { id: "bc", source: "b", target: "c", label: "0.91" } },
];

const layout = { name: "preset" };

//BACKEND: when we add to styles, we need to change it so we add an map with
//for new topuc: do node[parent= "or index"]
const style = [
  {
    selector: 'node[parent = "cluster1"]:child', // Only child nodes with clusterType tech
    style: {
      // This controls the INSIDE color of the circle (the background fill)
       "background-gradient-stop-colors": "#f093fb #f5576c",

    "shadow-color": "#f093fb",
     
    }
  },
  {
    selector: "node",
    style: {
      label: "data(label)",
      color: "#ffffff",
      "font-size": "24px",
      "font-weight": "700",
      "font-family": "Inter, system-ui, sans-serif",
      "background-gradient-direction": "to-bottom-right",
    "background-fill": "linear-gradient",
     
      width: 140,
      height: 140,
      "shape": "ellipse",
      "border-width": 3,
      
      "border-opacity": 1,
      "text-outline-color": "#000000",
      "text-outline-width": 2,
      "text-outline-opacity": 0.8,
      "shadow-blur": 25,
     
      "shadow-opacity": 0.7,
      "shadow-offset-x": 0,
      "shadow-offset-y": 6,
    },
  },
  {
    selector: "node[parent]",
    style: {
     
      "border-color": "#ec4899",
      "shadow-color": "#f093fb",
    },
  },
  {
    selector: ":parent",
    style: {
    
      "background-opacity": 0.2,
      "border-color": "#8b5cf6", 
      "border-width": 4,
      "border-style": "solid",
      "border-opacity": 0.8,
      "shape": "round-rectangle",
      padding: "50px",
      "font-size": "32px",
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
    },
  },
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
  {
    selector: "edge",
    style: {
      label: "data(label)",
      width: 4,
      "line-gradient-direction": "to-target",
      "line-gradient-stop-colors": "#a855f7 #ec4899",
      "target-arrow-color": "#ec4899",
      "target-arrow-shape": "triangle",
      "target-arrow-size": 16,
      "curve-style": "bezier",
      "font-size": "22px",
      "font-weight": "700",
      color: "#fbbf24",
      "text-background-gradient-direction": "to-bottom-right",
      "text-background-gradient-stop-colors": "#1e293b #334155",
      "text-background-opacity": 0.95,
      "text-background-padding": "8px",
      "text-background-shape": "round-rectangle",
      "text-border-color": "#a855f7",
      "text-border-width": 2,
      "text-border-opacity": 0.8,
      opacity: 0.9,
      "font-family": "Inter, system-ui, sans-serif",
      "text-outline-color": "#000000",
      "text-outline-width": 1,
      "text-outline-opacity": 0.6,
    },
  },
  {
    selector: "edge:hover",
    style: {
      width: 6,
     
    "shadow-color": "#f093fb",
      "line-gradient-stop-colors": "#06b6d4 #3b82f6",
      "target-arrow-color": "#3b82f6",
      opacity: 1,
      "transition-duration": "0.3s",
    },
  },
];

function App() {
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="text-center py-8">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent mb-4">
          Topic Similarity Graph
        </h1>
        <p className="text-slate-300 text-xl">Interactive visualization of document relationships</p>
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
              <button className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-200 shadow-lg">
                Reset Layout
              </button>
              <button className="w-full px-4 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg font-semibold hover:from-cyan-700 hover:to-blue-700 transition-all duration-200 shadow-lg">
                Center Graph
              </button>
              <button className="w-full px-4 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg font-semibold hover:from-emerald-700 hover:to-teal-700 transition-all duration-200 shadow-lg">
                Export PNG
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
                  <p className="text-slate-300 text-sm">ID</p>
                  <p className="text-white font-semibold">{selectedNode}</p>
                </div>
                <div className="p-3 bg-slate-700/50 rounded-lg">
                  <p className="text-slate-300 text-sm">Type</p>
                  <p className="text-white font-semibold">Document Node</p>
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
              stylesheet={style}
              cy={(cy) => {
                cy.on('tap', 'node', function(evt) {
                  const node = evt.target;
                  setSelectedNode(node.id());
                  console.log('Tapped node:', node.id());
                });
                
                cy.on('tap', 'edge', function(evt) {
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
              File Upload
            </h2>
           
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;