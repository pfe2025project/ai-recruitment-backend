# CV Management API Endpoints

This document outlines how to interact with the CV management endpoints, including uploading, fetching, deleting, and checking the status of a candidate's CV.

## Authentication

All endpoints require a valid Supabase JWT token in the `Authorization` header, prefixed with `Bearer `.

Example:
`Authorization: Bearer YOUR_SUPABASE_JWT_TOKEN`

## 1. Upload CV

Uploads a candidate's CV to Supabase Storage and processes its text content.

- **Endpoint:** `/api/cv/upload`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`

### Request Parameters

- `uid` (optional, Query Parameter): The UUID of the candidate. If not provided, the `uid` from the authenticated token will be used. **Note:** If provided, it must match the `uid` from the authenticated token.

### Request Body (multipart/form-data)

- `cv` (File): The CV file to upload. Allowed extensions: `.pdf`, `.doc`, `.docx`.

### Example Request (JavaScript - using Fetch API)

```javascript
const uploadCv = async (file, uid = null) => {
  const formData = new FormData();
  formData.append('cv', file);

  let url = '/api/cv/upload';
  if (uid) {
    url += `?uid=${uid}`;
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer YOUR_SUPABASE_JWT_TOKEN`,
        // 'Content-Type': 'multipart/form-data' is automatically set by FormData
      },
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      console.log('CV Upload successful:', data);
      return data;
    } else {
      console.error('CV Upload failed:', data.error);
      throw new Error(data.error || 'Failed to upload CV');
    }
  } catch (error) {
    console.error('Error during CV upload:', error);
    throw error;
  }
};

// Example usage:
// const cvFile = document.querySelector('input[type="file"]').files[0];
// uploadCv(cvFile, 'candidate-uuid-123');