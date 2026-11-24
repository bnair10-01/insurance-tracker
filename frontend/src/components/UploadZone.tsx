import { useDropzone } from 'react-dropzone'

interface Props {
  onFile: (file: File) => void
  disabled?: boolean
}

export function UploadZone({ onFile, disabled }: Props) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled,
    onDrop: (accepted) => {
      if (accepted[0]) onFile(accepted[0])
    },
  })

  return (
    <div
      {...getRootProps()}
      className={`cursor-pointer rounded-lg border-2 border-dashed p-12 text-center transition ${
        isDragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 bg-white hover:border-slate-400'
      } ${disabled ? 'pointer-events-none opacity-50' : ''}`}
    >
      <input {...getInputProps()} />
      <p className="font-medium text-slate-700">
        {isDragActive ? 'Drop the PDF here' : 'Drag a policy PDF here, or click to choose one'}
      </p>
      <p className="mt-1 text-sm text-slate-500">PDF only, up to 20MB</p>
    </div>
  )
}
