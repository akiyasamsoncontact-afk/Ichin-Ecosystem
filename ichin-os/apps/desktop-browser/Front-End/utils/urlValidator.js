// Ichin URL Validator
// Ensures all navigation stays within the Ichin network (.ichin TLD)

// Check if a URL is valid for Ichin network (must be .ichin domain)
export function isValidIchinUrl(url) {
  try {
    // Handle relative URLs (treat as Ichin)
    if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) {
      return true;
    }
    
    // Handle empty or invalid URLs
    if (!url || typeof url !== 'string') {
      return false;
    }
    
    // Parse the URL
    let parsedUrl;
    try {
      parsedUrl = new URL(url);
    } catch (e) {
      // If URL parsing fails, it's not a valid Ichin URL
      return false;
    }
    
    // Check if the hostname ends with .ichin
    const hostname = parsedUrl.hostname.toLowerCase();
    return hostname.endsWith('.ichin');
  } catch (error) {
    console.error('URL validation error:', error);
    return false;
  }
}

// Sanitize URL for Ichin network - if invalid, return a safe default
export function sanitizeUrl(url) {
  if (!url || typeof url !== 'string') {
    return '/'; // Default to home
  }
  
  if (isValidIchinUrl(url)) {
    return url;
  }
  
  // If it's a relative URL, return as is (it's already Ichin)
  if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) {
    return url;
  }
  
  // Otherwise, return home page
  return '/';
}

// Get the base Ichin URL for relative resolution
export function getIchinBaseUrl() {
  return window.location.origin;
}