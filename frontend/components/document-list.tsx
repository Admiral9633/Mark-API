"use client";

import { useEffect, useState } from "react";
import { FileText, Download, Clock, CheckCircle, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface Document {
  id: number;
  original_filename: string;
  created_at: string;
  status: "uploaded" | "processing" | "completed" | "error";
  marker_markdown?: string;
  pdf_file: string;
}

export function DocumentList() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/documents/`,
      );
      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      console.error("Fehler beim Laden der Dokumente:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: Document["status"]) => {
    const variants: Record<
      Document["status"],
      { icon: any; label: string; variant: any }
    > = {
      uploaded: { icon: Clock, label: "Hochgeladen", variant: "secondary" },
      processing: {
        icon: Clock,
        label: "Wird verarbeitet",
        variant: "default",
      },
      completed: {
        icon: CheckCircle,
        label: "Abgeschlossen",
        variant: "success",
      },
      error: { icon: XCircle, label: "Fehler", variant: "destructive" },
    };

    const { icon: Icon, label, variant } = variants[status];
    return (
      <Badge variant={variant as any} className="gap-1">
        <Icon className="w-3 h-3" />
        {label}
      </Badge>
    );
  };

  const downloadMarkdown = (doc: Document) => {
    if (!doc.marker_markdown) return;

    const blob = new Blob([doc.marker_markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${doc.original_filename.replace(".pdf", "")}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Dokumente</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-gray-500 py-8">Lädt...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Verarbeitete Dokumente</CardTitle>
      </CardHeader>
      <CardContent>
        {documents.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            Noch keine Dokumente hochgeladen
          </p>
        ) : (
          <div className="space-y-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1">
                  <FileText className="w-10 h-10 text-blue-500" />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      {doc.original_filename}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(doc.created_at).toLocaleString("de-DE")}
                    </p>
                  </div>
                  {getStatusBadge(doc.status)}
                </div>

                {doc.status === "completed" && doc.marker_markdown && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => downloadMarkdown(doc)}
                    className="ml-4"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Markdown
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
