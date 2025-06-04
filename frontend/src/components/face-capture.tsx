
"use client"

import { useRef, useEffect, useState, useCallback } from "react"
import { Camera } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FaceCaptureProps {
  onCapture: (imageData: string) => void
  onCancel: () => void
}

export function FaceCapture({ onCapture, onCancel }: FaceCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null)

  useEffect(() => {
    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: "user",
          },
        })

        if (videoRef.current) {
          videoRef.current.srcObject = stream
          setMediaStream(stream)
        }
      } catch (err) {
        console.error("Error accessing camera:", err)
      }
    }

    setupCamera()

    return () => {
      if (mediaStream) {
        mediaStream.getTracks().forEach((track) => track.stop())
      }
    }
  }, [mediaStream]) // Added mediaStream to dependencies

  const handleCapture = useCallback(() => {
    if (videoRef.current) {
      const canvas = document.createElement("canvas")
      canvas.width = videoRef.current.videoWidth
      canvas.height = videoRef.current.videoHeight

      const context = canvas.getContext("2d")
      if (context) {
        context.drawImage(videoRef.current, 0, 0)
        const imageData = canvas.toDataURL("image/jpeg", 0.8)
        onCapture(imageData)

        // Cleanup
        if (mediaStream) {
          mediaStream.getTracks().forEach((track) => track.stop())
        }
      }
    }
  }, [mediaStream, onCapture])

  const handleCancel = useCallback(() => {
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop())
    }
    onCancel()
  }, [mediaStream, onCancel])

  return (
    <div className="relative rounded-lg overflow-hidden bg-muted">
      <video ref={videoRef} autoPlay playsInline className="w-full aspect-video object-cover" />
      <div className="absolute inset-x-0 bottom-4 flex justify-center gap-4">
        <Button type="button" variant="outline" className="bg-background shadow-lg" onClick={handleCancel}>
          Cancel
        </Button>
        <Button type="button" className="bg-primary shadow-lg" onClick={handleCapture}>
          <Camera className="mr-2 h-4 w-4" />
          Capture Photo
        </Button>
      </div>
    </div>
  )
}

