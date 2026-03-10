import { useState } from 'react';
import FileUploader from './components/FileUploader.jsx';
import ChatInterface from './components/ChatInterface.jsx';

export default function App() {
  const [isUploaded, setIsUploaded] = useState(false);
  const [filename, setFilename] = useState("");

  const handleUploadSuccess = (name) => {
    setFilename(name);
    setIsUploaded(true);
  };

  return (
    <div className="min-h-screen w-full bg-[#F5F5F0] text-stone-800 font-sans flex flex-col items-center justify-start pt-20 px-6">

      {/* Added text-center and mx-auto to ensure centering */}
      <div className="w-full max-w-3xl flex flex-col items-center text-center mx-auto">
        {/* Minimalist Heading */}
        <h1 className="text-4xl md:text-5xl font-serif font-medium mb-6 text-stone-900 tracking-tight">
          {isUploaded ? filename : "Upload Document"}
        </h1>

        <p className="text-stone-500 mb-12 text-lg max-w-lg leading-relaxed font-light mx-auto">
          {isUploaded
            ? "Ask questions, get summaries, and uncover insights."
            : "Upload your document to begin the conversation."}
        </p>

        {!isUploaded ? (
          <div className="w-full max-w-xl mx-auto">
            <FileUploader onUploadSuccess={handleUploadSuccess} />
          </div>
        ) : (
          <div className="w-full flex flex-col items-center gap-8">
            <ChatInterface />
            <button
              onClick={() => setIsUploaded(false)}
              className="text-stone-400 hover:text-stone-900 transition-colors text-sm font-medium tracking-wide uppercase border-b border-transparent hover:border-stone-900 pb-0.5"
            >
              Upload New File
            </button>
          </div>
        )}
      </div>

    </div>
  );
}
