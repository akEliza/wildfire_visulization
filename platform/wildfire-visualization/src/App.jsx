import React, { useState } from "react";

const variables = ["theta", "rhof", "velocity", "vorticity"];
const terrains = [
  "headcurve40",
  "headcurve80",
  "headcurve320",
  "backcurve40",
  "backcurve80",
  "backcurve320",
  "valley_losAlamos"
];

export default function App() {
  const [selectedVar, setSelectedVar] = useState("rhof");
  const [selectedTerrain, setSelectedTerrain] = useState("headcurve40");

  const fileExt = selectedVar === "rhof" ? "png" : "mp4";
  const filePath = `results/${selectedVar}/${selectedTerrain}.${fileExt}`;

  return (
    <div className="min-h-screen bg-gray-100 p-6 font-sans">
      <h1 className="text-3xl font-bold mb-6 text-center">Wildfire Visualization</h1>

      <div className="flex justify-center space-x-4 mb-8">
        <select
          value={selectedVar}
          onChange={(e) => setSelectedVar(e.target.value)}
          className="border border-gray-300 rounded px-4 py-2 shadow-sm text-xl font-semibold"
        >
          {variables.map((v) => (
            <option key={v} value={v}>{v}</option>
          ))}
        </select>

        <select
          value={selectedTerrain}
          onChange={(e) => setSelectedTerrain(e.target.value)}
          className="border border-gray-300 rounded px-4 py-2 shadow-sm text-xl font-semibold"
        >
          {terrains.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      <div className="max-w-4xl mx-auto border rounded-lg bg-white shadow p-4">
        {selectedVar === "rhof" ? (
          <img src={filePath} alt="Visualization" className="w-full h-auto" />
        ) : (
          <video key={filePath} controls className="w-full h-auto">
            <source src={filePath} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        )}
      </div>
    </div>
  );
}
