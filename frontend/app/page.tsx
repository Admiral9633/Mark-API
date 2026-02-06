"use client";

import { useState } from "react";
import { UploadZone } from "@/components/upload-zone";
import { DocumentList } from "@/components/document-list";

export default function Home() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = () => {
    // Trigger refresh of document list
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              📄 PDF OCR System
            </h1>
            <p className="text-gray-600">
              Hochladen und verarbeiten Sie PDFs mit lokaler OCR-Technologie
            </p>
          </div>

          <div className="grid gap-8">
            <UploadZone onUploadSuccess={handleUploadSuccess} />
            <DocumentList key={refreshKey} />
          </div>
        </div>
      </div>
    </main>
  );
}
