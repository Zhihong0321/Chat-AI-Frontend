# Frontend Integration Guide - GPT-5 Document Processing

## Overview

The backend now supports advanced document processing using GPT-5 Vision for PDFs and images. This guide covers the API changes and UI recommendations for frontend integration.

## API Changes

### 1. New Document Processing Endpoint

#### POST /documents/process-with-gpt5

Process documents using GPT-5 Vision for enhanced text extraction and analysis.

**Endpoint:**
```
POST https://eternalgy-rag-ai-production.up.railway.app/documents/process-with-gpt5
```

**Request:**
```http
POST /documents/process-with-gpt5
Content-Type: multipart/form-data

file: [binary file data]
```

**Supported Formats:**
- PDF files (`.pdf`)
- Images (`.png`, `.jpg`, `.jpeg`)

**Response (Success):**
```json
{
  "doc_id": "uuid",
  "filename": "document.pdf",
  "processing_method": "gpt5_vision",
  "extracted_text": "Full extracted text content...",
  "extracted_text_preview": "First 500 characters...",
  "page_count": 5,
  "status": "processed",
  "timestamp": "2025-11-12T05:00:00Z"
}
```

**Response (Error):**
```json
{
  "detail": "Unsupported file format. Supported: PDF, PNG, JPG, JPEG"
}
```

**When to Use:**
- Documents that need OCR (scanned PDFs, images)
- Documents with complex layouts or tables
- Documents requiring visual understanding
- Images with text content

### 2. Enhanced Upload Response

The existing `/ingest/upload` endpoint now includes additional fields:

**Endpoint:**
```
POST https://eternalgy-rag-ai-production.up.railway.app/ingest/upload
```

**Enhanced Response:**
```json
{
  "doc_id": "uuid",
  "title": "document.pdf",
  "status": "parsed",
  "uploaded_at": "2025-11-12T05:00:00Z",
  "processing_method": "gpt5_vision",
  "extracted_text_preview": "First 500 characters of extracted text...",
  "metadata": {
    "file_size": 12345,
    "file_type": "application/pdf",
    "page_count": 5
  }
}
```

**New Fields:**
- `processing_method` - Shows which method was used (`gpt5_vision`, `unstructured`, `fallback`)
- `extracted_text_preview` - First 500 chars for immediate feedback
- `metadata` - Additional file information

### 3. Health Check Updates

The `/health` endpoint now reports document processing capabilities:

**Endpoint:**
```
GET https://eternalgy-rag-ai-production.up.railway.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T05:00:00Z",
  "components": {
    "api": "healthy",
    "database": "healthy",
    "document_processing": {
      "status": "healthy",
      "gpt5_available": true,
      "supported_formats": ["pdf", "png", "jpg", "jpeg", "docx", "txt", "md", "csv", "xlsx"]
    }
  }
}
```

**Check on Startup:**
```javascript
// Example: Check if GPT-5 vision is available
const response = await fetch('https://eternalgy-rag-ai-production.up.railway.app/health');
const health = await response.json();

if (health.components?.document_processing?.gpt5_available) {
  console.log('✅ GPT-5 Vision processing available');
} else {
  console.warn('⚠️ GPT-5 Vision not configured - using fallback methods');
}
```

## UI Recommendations

### 1. File Upload Enhancements

#### Client-Side Validation

```javascript
const SUPPORTED_FORMATS = {
  'application/pdf': '.pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'text/plain': '.txt',
  'text/markdown': '.md',
  'text/csv': '.csv',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
  'image/png': '.png',
  'image/jpeg': '.jpg, .jpeg'
};

function validateFile(file) {
  const maxSize = 40 * 1024 * 1024; // 40MB
  
  if (file.size > maxSize) {
    return { valid: false, error: 'File size exceeds 40MB limit' };
  }
  
  if (!SUPPORTED_FORMATS[file.type]) {
    return { 
      valid: false, 
      error: `Unsupported format. Supported: ${Object.values(SUPPORTED_FORMATS).join(', ')}` 
    };
  }
  
  return { valid: true };
}
```

#### Processing Indicator

Show different indicators based on file type:

```javascript
function getProcessingMessage(file) {
  const isPdfOrImage = ['application/pdf', 'image/png', 'image/jpeg'].includes(file.type);
  
  if (isPdfOrImage) {
    return '🔍 Processing with AI Vision...';
  } else {
    return '📄 Processing document...';
  }
}
```

### 2. Upload Status Display

#### Show Processing Method

```html
<!-- After successful upload -->
<div class="upload-result">
  <span class="status-icon">✅</span>
  <span class="filename">document.pdf</span>
  <span class="processing-badge">Processed with GPT-5 Vision</span>
</div>
```

#### Display Text Preview

```html
<!-- Show extracted text preview -->
<div class="text-preview">
  <h4>Extracted Text Preview:</h4>
  <p class="preview-text">{{ extracted_text_preview }}</p>
  <button onclick="showFullText()">View Full Text</button>
</div>
```

### 3. Error Handling

#### Graceful Error Messages

```javascript
async function uploadDocument(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(
      'https://eternalgy-rag-ai-production.up.railway.app/ingest/upload',
      {
        method: 'POST',
        body: formData
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }
    
    const result = await response.json();
    return result;
    
  } catch (error) {
    // Show user-friendly error
    if (error.message.includes('Unsupported file format')) {
      showError('This file type is not supported. Please upload PDF, DOCX, TXT, MD, CSV, XLSX, PNG, or JPG files.');
    } else if (error.message.includes('size')) {
      showError('File is too large. Maximum size is 40MB.');
    } else {
      showError(`Upload failed: ${error.message}`);
    }
  }
}
```

### 4. Visual Feedback

#### Processing States

```javascript
const UPLOAD_STATES = {
  IDLE: 'idle',
  VALIDATING: 'validating',
  UPLOADING: 'uploading',
  PROCESSING: 'processing',
  SUCCESS: 'success',
  ERROR: 'error'
};

function updateUploadUI(state, data = {}) {
  switch(state) {
    case UPLOAD_STATES.VALIDATING:
      showMessage('🔍 Validating file...');
      break;
    case UPLOAD_STATES.UPLOADING:
      showMessage('⬆️ Uploading...');
      showProgress(data.progress);
      break;
    case UPLOAD_STATES.PROCESSING:
      const isPdfOrImage = data.file?.type?.includes('pdf') || data.file?.type?.includes('image');
      showMessage(isPdfOrImage ? '🤖 Processing with AI Vision...' : '📄 Processing document...');
      break;
    case UPLOAD_STATES.SUCCESS:
      showMessage(`✅ ${data.filename} uploaded successfully!`);
      if (data.processing_method === 'gpt5_vision') {
        showBadge('Processed with GPT-5 Vision');
      }
      if (data.extracted_text_preview) {
        showPreview(data.extracted_text_preview);
      }
      break;
    case UPLOAD_STATES.ERROR:
      showMessage(`❌ ${data.error}`);
      break;
  }
}
```

## Implementation Examples

### Example 1: Basic Upload with Gradio

```python
import gradio as gr
import httpx

API_BASE = "https://eternalgy-rag-ai-production.up.railway.app"

def upload_document(file_path):
    if not file_path:
        return "Please select a file"
    
    try:
        # Show processing message based on file type
        file_ext = file_path.lower().split('.')[-1]
        if file_ext in ['pdf', 'png', 'jpg', 'jpeg']:
            status_msg = "🤖 Processing with AI Vision..."
        else:
            status_msg = "📄 Processing document..."
        
        # Upload file
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = httpx.post(
                f"{API_BASE}/ingest/upload",
                files=files,
                timeout=60.0
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # Build success message
            msg = f"✅ Uploaded successfully!\n"
            msg += f"Document ID: {result['doc_id']}\n"
            msg += f"Status: {result['status']}\n"
            
            if result.get('processing_method'):
                msg += f"Processing Method: {result['processing_method']}\n"
            
            if result.get('extracted_text_preview'):
                msg += f"\n📄 Text Preview:\n{result['extracted_text_preview'][:200]}..."
            
            return msg
        else:
            return f"❌ Upload failed: {response.text}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# Document Upload with GPT-5 Vision")
    
    file_upload = gr.File(
        label="Upload Document",
        file_types=[".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx", ".png", ".jpg"],
        type="filepath"
    )
    upload_btn = gr.Button("Upload", variant="primary")
    status_output = gr.Textbox(label="Status", lines=10)
    
    upload_btn.click(
        upload_document,
        inputs=[file_upload],
        outputs=[status_output]
    )
```

### Example 2: Check GPT-5 Availability

```python
def check_gpt5_availability():
    try:
        response = httpx.get(f"{API_BASE}/health", timeout=5.0)
        if response.status_code == 200:
            health = response.json()
            doc_processing = health.get('components', {}).get('document_processing', {})
            
            if doc_processing.get('gpt5_available'):
                return "✅ GPT-5 Vision is available and configured"
            else:
                return "⚠️ GPT-5 Vision is not configured - using fallback methods"
        else:
            return "❌ Cannot check health status"
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

### Example 3: Advanced Upload with Preview

```python
def upload_with_preview(file_path):
    if not file_path:
        return "Please select a file", ""
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = httpx.post(
                f"{API_BASE}/ingest/upload",
                files=files,
                timeout=60.0
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # Status message
            status = f"✅ Uploaded: {result['title']}\n"
            status += f"Status: {result['status']}\n"
            
            if result.get('processing_method') == 'gpt5_vision':
                status += "🤖 Processed with GPT-5 Vision\n"
            
            # Preview text
            preview = result.get('extracted_text_preview', 'No preview available')
            
            return status, preview
        else:
            return f"❌ Upload failed: {response.text}", ""
            
    except Exception as e:
        return f"❌ Error: {str(e)}", ""

# Gradio interface with preview
with gr.Blocks() as app:
    with gr.Row():
        with gr.Column():
            file_upload = gr.File(label="Upload Document")
            upload_btn = gr.Button("Upload")
            status_output = gr.Textbox(label="Status", lines=5)
        
        with gr.Column():
            preview_output = gr.Textbox(
                label="Extracted Text Preview",
                lines=15,
                max_lines=20
            )
    
    upload_btn.click(
        upload_with_preview,
        inputs=[file_upload],
        outputs=[status_output, preview_output]
    )
```

## Testing

### Test Files Reference

The backend repository includes test files you can use:

- `test_gpt5_nano_document_processing.py` - Shows expected request/response formats
- `GPT5_DOCUMENTATION_COMPLETE.md` - Full API documentation

### Manual Testing Checklist

- [ ] Upload PDF file - should use GPT-5 vision
- [ ] Upload image (PNG/JPG) - should use GPT-5 vision
- [ ] Upload DOCX file - should use standard processing
- [ ] Upload TXT file - should use standard processing
- [ ] Try unsupported format - should show clear error
- [ ] Try file > 40MB - should show size error
- [ ] Check health endpoint on app startup
- [ ] Verify extracted text preview displays correctly
- [ ] Verify processing method badge shows correctly

## Environment Requirements

### Frontend Startup Checks

```python
def verify_backend_ready():
    """Check backend is properly configured on app startup."""
    try:
        response = httpx.get(f"{API_BASE}/health", timeout=5.0)
        
        if response.status_code != 200:
            print("⚠️ WARNING: Backend health check failed")
            return False
        
        health = response.json()
        
        # Check document processing
        doc_proc = health.get('components', {}).get('document_processing', {})
        
        if not doc_proc.get('gpt5_available'):
            print("⚠️ WARNING: GPT-5 Vision not configured")
            print("   Documents will be processed with fallback methods")
        
        # Check required components
        components = health.get('components', {})
        for component, status in components.items():
            if isinstance(status, dict):
                status = status.get('status', 'unknown')
            
            if status != 'healthy':
                print(f"⚠️ WARNING: {component} is {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to backend: {e}")
        return False

# Run on app startup
if __name__ == "__main__":
    print("🚀 Starting frontend...")
    
    if verify_backend_ready():
        print("✅ Backend is ready")
        app.launch()
    else:
        print("❌ Backend is not ready - check configuration")
        # Optionally: launch anyway with warnings
        app.launch()
```

## Error Codes Reference

| HTTP Code | Meaning | User Message |
|-----------|---------|--------------|
| 200 | Success | Document uploaded successfully |
| 400 | Bad Request | Invalid file or parameters |
| 413 | Payload Too Large | File exceeds 40MB limit |
| 415 | Unsupported Media Type | File format not supported |
| 500 | Internal Server Error | Processing failed - try again |
| 503 | Service Unavailable | Backend is temporarily unavailable |

## Best Practices

1. **Always validate files client-side** before uploading
2. **Show processing indicators** for better UX
3. **Display extracted text previews** when available
4. **Check health endpoint** on app startup
5. **Handle errors gracefully** with user-friendly messages
6. **Show processing method badges** to inform users
7. **Implement retry logic** for transient failures
8. **Cache health check results** (refresh every 5 minutes)

## Support

For questions or issues:
- Check API documentation: https://eternalgy-rag-ai-production.up.railway.app/docs
- Review backend test files for examples
- Use health endpoint to diagnose issues
- Check backend logs on Railway dashboard

## Summary

The GPT-5 Vision integration enhances document processing with:
- ✅ Better OCR for scanned documents
- ✅ Visual understanding of complex layouts
- ✅ Improved text extraction from images
- ✅ Automatic format detection and processing
- ✅ Real-time processing feedback

Update your frontend to take advantage of these features for a better user experience!
