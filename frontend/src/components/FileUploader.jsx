import { useState } from "react";
import axios from "axios";

export default function FileUploader({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  function handleFileChange(e) {
    if (e.target.files) {
      setFile(e.target.files[0]);
      setError(null);
    }
  }

  async function handleUpload() {
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("http://localhost:8000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      if (onUploadSuccess) {
        onUploadSuccess(file.name);
      }
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.detail || "Failed to upload file. Please try again.";
      setError(msg);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="space-y-8">
      <div className="relative group p-8 border-2 border-dashed border-stone-300 rounded-xl hover:border-stone-500 transition-colors bg-white/50 cursor-pointer text-center">
        <label className="block w-full h-full cursor-pointer flex flex-col items-center justify-center gap-3">
          <input
            type="file"
            accept=".csv, .pdf, .jpg, .jpeg, .png, .bmp, .gif"
            onChange={handleFileChange}
            className="hidden"
          />
          <span className="text-3xl text-stone-400 group-hover:text-stone-600 transition-colors">📄</span>
          <span className="text-sm font-medium text-stone-500 group-hover:text-stone-800 transition-colors">
            Click to select a file
          </span>
          <span className="text-xs text-stone-400">PDF, Word, Excel, CSV</span>
        </label>
      </div>

      {file && (
        <div className="flex items-center justify-between p-4 bg-white border border-stone-200 rounded-lg shadow-sm">
          <div className="flex items-center gap-3 overflow-hidden">
            <span className="text-xl">📎</span>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-semibold text-stone-800 truncate">{file.name}</span>
              <span className="text-xs text-stone-500 font-mono">{(file.size / 1024).toFixed(2)} KB</span>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 text-red-600 border-l-4 border-red-500 text-sm">
          {error}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className={`w-full py-4 rounded-lg font-semibold text-sm tracking-widest uppercase transition-all duration-200 ${!file || uploading
            ? "bg-stone-200 text-stone-400 cursor-not-allowed"
            : "bg-stone-900 text-white hover:bg-black shadow-lg hover:shadow-xl hover:-translate-y-0.5"
          }`}
      >
        {uploading ? "Processing..." : "Start Analysis"}
      </button>
    </div>
  );
}
