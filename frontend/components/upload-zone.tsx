'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useToast } from '@/components/ui/use-toast'

interface UploadZoneProps {
  onUploadSuccess?: () => void
}

export function UploadZone({ onUploadSuccess }: UploadZoneProps) {
  const [isUploading, setIsUploading] = useState(false)
  const { toast } = useToast()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append('pdf_file', file)

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/documents/convert/`,
        {
          method: 'POST',
          body: formData,
        }
      )

      if (!response.ok) {
        throw new Error('Upload fehlgeschlagen')
      }

      const data = await response.json()

      toast({
        title: '✅ Erfolg',
        description: `${file.name} wurde erfolgreich verarbeitet`,
      })

      onUploadSuccess?.()
    } catch (error) {
      toast({
        title: '❌ Fehler',
        description: 'Upload fehlgeschlagen. Bitte versuchen Sie es erneut.',
        variant: 'destructive',
      })
    } finally {
      setIsUploading(false)
    }
  }, [toast, onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    disabled: isUploading,
  })

  return (
    <Card>
      <CardContent className="pt-6">
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
            transition-colors duration-200
            ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
            ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center gap-4">
            {isUploading ? (
              <>
                <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
                <p className="text-lg font-medium text-gray-700">
                  Wird verarbeitet...
                </p>
              </>
            ) : (
              <>
                {isDragActive ? (
                  <FileText className="w-12 h-12 text-blue-500" />
                ) : (
                  <Upload className="w-12 h-12 text-gray-400" />
                )}
                <div>
                  <p className="text-lg font-medium text-gray-700 mb-1">
                    PDF-Datei hier ablegen oder klicken zum Auswählen
                  </p>
                  <p className="text-sm text-gray-500">
                    Maximale Dateigröße: 50MB
                  </p>
                </div>
                <Button type="button" variant="secondary">
                  Datei auswählen
                </Button>
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
