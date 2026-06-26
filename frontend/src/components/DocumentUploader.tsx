import React, { useState } from 'react';
import { ingestFile } from '../api/aiApi';
import { toast } from 'react-toastify';

interface DocumentUploaderProps {
  sessionId: string;
}

const DocumentUploader: React.FC<DocumentUploaderProps> = ({ sessionId }) => {
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    setUploadProgress(0);
    setIsUploading(true);
    setSuccessMessage(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Authentication token not found. Please log in again.');
      }

      const xhr = new XMLHttpRequest();
      xhr.open('POST', `${import.meta.env.VITE_API_BASE_URL}/api/documents/upload`);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.setRequestHeader('Accept', 'application/json');

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(progress);
        }
      };

      xhr.onload = () => {
        setIsUploading(false);
        if (xhr.status >= 200 && xhr.status < 300) {
          const contentType = xhr.getResponseHeader('Content-Type');
          if (contentType && contentType.includes('application/json')) {
            const response = JSON.parse(xhr.responseText);
            setSuccessMessage(`✓ Indexed ${response.chunks_indexed} chunks`);
          } else {
            throw new Error('Unexpected response format from server.');
          }
        } else {
          const contentType = xhr.getResponseHeader('Content-Type');
          if (contentType && contentType.includes('application/json')) {
            const errorResponse = JSON.parse(xhr.responseText);
            throw new Error(errorResponse.message || 'File upload failed.');
          } else {
            throw new Error('File upload failed with an unknown error.');
          }
        }
      };

      xhr.onerror = () => {
        setIsUploading(false);
        throw new Error('Network error occurred during file upload.');
      };

      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', sessionId);

      xhr.send(formData);
    } catch (error: any) {
      setIsUploading(false);
      toast.error(error.message || 'An error occurred during file upload.');
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  return (
    <div
      className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-blue-500"
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept=".xlsx,.xls,.pdf,.docx"
        className="hidden"
        id="file-upload"
        onChange={handleFileSelect}
      />
      <label htmlFor="file-upload" className="block text-gray-600">
        Drag and drop a file here, or <span className="text-blue-500 underline">browse</span> to upload
      </label>
      {isUploading && (
        <div className="mt-4">
          <div className="relative w-full h-4 bg-gray-200 rounded">
            <div
              className="absolute top-0 left-0 h-4 bg-blue-500 rounded"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">{uploadProgress}%</p>
        </div>
      )}
      {successMessage && (
        <div className="mt-4 text-green-600 font-semibold">{successMessage}</div>
      )}
    </div>
  );
};

export default DocumentUploader;