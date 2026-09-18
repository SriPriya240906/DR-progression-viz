import { ImagePlus, X } from 'lucide-react';

export function ImageUpload({ 
  file, 
  previewUrl, 
  onFileSelect, 
  onRemove, 
  onAnalyze, 
  isLoading, 
  disabled, 
  analyzeButtonText = 'Analyze Image',
  uploadOnly = false 
}) {
  return (
    <section className="upload-panel">
      <label className="drop-zone" htmlFor="retinal-file">
        <input id="retinal-file" type="file" accept="image/png,image/jpeg,image/jpg" onChange={onFileSelect} />
        {previewUrl ? (
          <img src={previewUrl} alt="Selected retinal image preview" />
        ) : (
          <div className="upload-placeholder">
            <ImagePlus size={28} />
            <span>Upload Retinal Image</span>
            <small>PNG • JPG • JPEG</small>
          </div>
        )}
      </label>

      <div className="upload-details">
        <p className="eyebrow">Retinal Screening Workspace</p>
        <h3>{file ? file.name : 'No image selected yet'}</h3>
        {file && (
          <div className="upload-meta">
            <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
            <button type="button" className="inline-remove" onClick={onRemove} aria-label="Remove uploaded file">
              <X size={14} /> Remove
            </button>
          </div>
        )}
        <p className="upload-copy">
          {uploadOnly 
            ? 'Upload a fundus image to begin the 4-stage analysis workflow. Image quality will be assessed first before disease prediction.'
            : 'Click "Analyze Image Quality" to assess the uploaded image and determine if enhancement is needed before disease analysis.'
          }
        </p>

        {!uploadOnly && onAnalyze && (
          <div className="action-row">
            <button className="primary-button" type="button" onClick={onAnalyze} disabled={isLoading || disabled || !file}>
              {isLoading ? 'Analyzing...' : analyzeButtonText}
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
