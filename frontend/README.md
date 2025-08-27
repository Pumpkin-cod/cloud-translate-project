# 🌐 Cloud Translate Frontend

A modern, responsive web interface for the Cloud Translate API. Built with vanilla HTML, CSS, and JavaScript - no frameworks required.

## 🎯 What Was Built

**Single-Page Application** that connects directly to the AWS serverless backend:
- **Real-time translation** using AWS Translate service
- **10+ language support** with intuitive dropdowns
- **Modern gradient UI** with smooth animations and loading states
- **Responsive design** that works on all devices
- **Input validation** and error handling
- **Direct API integration** with proper CORS handling

## 🚀 Quick Start

**Local Development:**
```bash
# Serve locally
python3 -m http.server 8000
# Visit: http://localhost:8000
```

**Deploy to Vercel:**
```bash
npx vercel --prod
```

## ⚙️ Configuration

The API endpoint is configured in `index.html`:
```javascript
const API_ENDPOINT = 'https://tdns0znam4.execute-api.us-east-1.amazonaws.com/dev/translate';
```

Update this URL to point to your deployed API Gateway endpoint.

## 🎨 Key Features

- **Zero Dependencies** - Pure HTML/CSS/JavaScript
- **Mobile-First Design** - Responsive across all screen sizes
- **Real AWS Integration** - Connects to actual AWS Translate service
- **User-Friendly** - Clear feedback, loading states, error messages
- **Production Ready** - Optimized for deployment

---

**Live Demo:** https://cloud-translate-project-m7ui.vercel.app  
**Backend API:** https://tdns0znam4.execute-api.us-east-1.amazonaws.com/dev/translate