import { useState, useRef } from 'react';
import { Bug, Upload } from 'lucide-react';
import API from '../api';

// ── Image Quality Thresholds ──
const MIN_WIDTH = 224;
const MIN_HEIGHT = 224;
const MIN_FILE_SIZE_KB = 10;       // Real photos are always > 10KB
const BLUR_THRESHOLD = 100;        // Laplacian variance — higher = stricter
const MIN_UNIQUE_COLORS = 500;     // Real photos have thousands of unique colors; pixel art has < 100

/**
 * Compute the Laplacian variance of a greyscale image drawn onto a canvas.
 * A low variance means the image lacks sharp edges → blurry.
 */
function computeBlurScore(ctx, size) {
  const { data } = ctx.getImageData(0, 0, size, size);

  // Convert to greyscale
  const grey = new Float32Array(size * size);
  for (let i = 0; i < grey.length; i++) {
    const idx = i * 4;
    grey[i] = 0.299 * data[idx] + 0.587 * data[idx + 1] + 0.114 * data[idx + 2];
  }

  // Apply 3×3 Laplacian kernel [ 0,-1,0 / -1,4,-1 / 0,-1,0 ]
  let sum = 0;
  let sumSq = 0;
  let count = 0;
  for (let y = 1; y < size - 1; y++) {
    for (let x = 1; x < size - 1; x++) {
      const lap =
        4 * grey[y * size + x] -
        grey[(y - 1) * size + x] -
        grey[(y + 1) * size + x] -
        grey[y * size + (x - 1)] -
        grey[y * size + (x + 1)];
      sum += lap;
      sumSq += lap * lap;
      count++;
    }
  }
  const mean = sum / count;
  return sumSq / count - mean * mean;
}

/**
 * Count unique colors in the image. Real photographs contain thousands
 * of distinct colors. Pixel art, clipart, and upscaled low-res images
 * contain very few because large blocks share the exact same color.
 */
function countUniqueColors(ctx, size) {
  const { data } = ctx.getImageData(0, 0, size, size);
  const colorSet = new Set();
  for (let i = 0; i < data.length; i += 4) {
    // Quantize to reduce noise: group colors into bins of 4
    const r = data[i] >> 2;
    const g = data[i + 1] >> 2;
    const b = data[i + 2] >> 2;
    colorSet.add((r << 16) | (g << 8) | b);
  }
  return colorSet.size;
}

/**
 * Full image quality validation pipeline.
 * Returns { ok: true } or { ok: false, reason: string }.
 */
function validateImageQuality(file) {
  return new Promise((resolve) => {
    // 1. File size check — tiny files can't be real photos
    const fileSizeKB = file.size / 1024;
    if (fileSizeKB < MIN_FILE_SIZE_KB) {
      resolve({
        ok: false,
        reason: `📐 Image file is too small (${fileSizeKB.toFixed(1)}KB). Please upload a real photograph of a leaf.`,
      });
      return;
    }

    const img = new Image();
    img.onload = () => {
      const w = img.naturalWidth;
      const h = img.naturalHeight;

      // 2. Resolution check
      if (w < MIN_WIDTH || h < MIN_HEIGHT) {
        resolve({
          ok: false,
          reason: `📐 Image resolution too low (${w}×${h}). Please upload an image that is at least ${MIN_WIDTH}×${MIN_HEIGHT} pixels.`,
        });
        return;
      }

      // Draw once into a canvas, reuse for all checks
      const canvas = document.createElement('canvas');
      const size = 256;
      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, size, size);

      // 3. Unique color count — catches pixel art, clipart, upscaled thumbnails
      const uniqueColors = countUniqueColors(ctx, size);
      if (uniqueColors < MIN_UNIQUE_COLORS) {
        resolve({
          ok: false,
          reason: '🎨 This image appears to be pixel art, a clipart, or a very low-quality image. Please upload a real, high-resolution photograph of a leaf.',
        });
        return;
      }

      // 4. Blur / sharpness check
      const blurScore = computeBlurScore(ctx, size);
      if (blurScore < BLUR_THRESHOLD) {
        resolve({
          ok: false,
          reason: '🔍 Image appears too blurry. Please upload a clear, focused photo of the leaf.',
        });
        return;
      }

      resolve({ ok: true });
    };
    img.onerror = () => resolve({ ok: false, reason: 'Could not read the image file.' });
    img.src = URL.createObjectURL(file);
  });
}

export default function LeafDisease() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef();

  const handleFile = async (e) => {
    const f = e.target.files[0];
    if (!f) return;

    setError('');
    setResult(null);

    // Run quality validation before accepting the file
    const validation = await validateImageQuality(f);
    if (!validation.ok) {
      setError(validation.reason);
      setFile(null);
      setPreview('');
      // Reset the input so the same file can be re-selected after fixing
      inputRef.current.value = '';
      return;
    }

    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) { setError('Please upload a leaf image.'); return; }
    setError(''); setResult(null); setLoading(true);
    try {
      const fd = new FormData();
      fd.append('file', file);
      const uid = localStorage.getItem('user_id');
      if (uid) fd.append('user_id', uid);
      const res = await API.post('/detect_disease/', fd);
      
      // Adjusted Legitimacy Logic: 
      // - Below 30%: Almost certainly NOT a leaf (Reject).
      // - 30% to 60%: Possibly a leaf, but AI is unsure (Show with Badge).
      // - Above 60%: High confidence (Show normally).
      
      if (res.data.confidence < 0.30) {
        setError('🔍 Image not recognized. Please ensure the leaf is well-lit and centered in the photo.');
        setResult(null);
      } else {
        setResult(res.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Our system was unable to analyze this image. Please try another photo.');
    } finally { setLoading(false); }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1>🍃 Leaf Disease Detection</h1>
        <p>Upload a leaf image to detect diseases using AI</p>
      </div>
      <div className="glass-card" style={{ maxWidth: 550, margin: '0 auto', padding: 40 }}>
        {error && <div className="alert alert-error animate-fade-in">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div
            onClick={() => inputRef.current.click()}
            style={{
              border: '2px dashed var(--border-glass)',
              borderRadius: 'var(--radius)',
              padding: preview ? 0 : '48px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'var(--transition)',
              overflow: 'hidden',
              marginBottom: 20,
            }}
          >
            {preview ? (
              <img src={preview} alt="Leaf preview" style={{ width: '100%', display: 'block', borderRadius: 'var(--radius-sm)' }} />
            ) : (
              <>
                <Upload size={32} style={{ color: 'var(--text-muted)', marginBottom: 12 }} />
                <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>Click to upload or drag a leaf image</p>
                <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>JPEG, PNG up to 10MB</p>
              </>
            )}
            <input ref={inputRef} type="file" accept="image/*" onChange={handleFile} style={{ display: 'none' }} />
          </div>
          <button className="btn-primary" type="submit" disabled={loading} style={{ width: '100%' }}>
            {loading ? <div className="spinner" /> : <><Bug size={18} /> Detect Disease</>}
          </button>
        </form>
        {result && (
          <div className="animate-fade-in" style={{ marginTop: 32 }}>
            <div className="result-box" style={{ textAlign: 'center', padding: '24px' }}>
              <p style={{ fontSize: 13, marginBottom: 8, color: 'var(--text-secondary)' }}>Analysis Result</p>
              <h2 style={{ fontSize: '2rem', color: '#ef4444', margin: 0 }}>{result.disease}</h2>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginTop: 8 }}>
                <p style={{ margin: 0, fontSize: 14 }}>Confidence: {(result.confidence * 100).toFixed(1)}%</p>
                {result.confidence < 0.60 && (
                  <span style={{ fontSize: '10px', background: '#fff3cd', color: '#856404', padding: '2px 8px', borderRadius: '10px', fontWeight: 'bold' }}>⚠️ Low Confidence</span>
                )}
              </div>
            </div>

            <div style={{ border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: 16, marginTop: 20, overflow: 'hidden' }}>
                <div style={{ padding: 16, background: 'rgba(239, 68, 68, 0.05)' }}>
                    <h4 style={{ fontSize: 14, color: '#ef4444', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 8 }}>💊 Immediate Treatment</h4>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{result.treatment}</p>
                </div>
                <div style={{ padding: 16, background: '#fff', borderTop: '1px solid rgba(239, 68, 68, 0.1)' }}>
                    <h4 style={{ fontSize: 14, color: 'var(--olive-green)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 8 }}>🛡️ Prevention Strategy</h4>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{result.prevention}</p>
                </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
