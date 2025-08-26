# 🌍 Cloud Translate Frontend

A beautiful, modern web interface for the Cloud Translate API built with vanilla HTML, CSS, and JavaScript.

## ✨ Features

- **Modern Design** - Clean gradient UI with smooth animations
- **Multi-Language Support** - 10+ languages including English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, and Chinese
- **Real-Time Translation** - Instant translation using AWS Translate service
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Error Handling** - User-friendly error messages and validation
- **Loading States** - Visual feedback during translation process

## 🚀 Quick Start

### Local Development

1. **Open directly in browser:**
   ```bash
   open index.html
   ```

2. **Or serve locally:**
   ```bash
   # Using Python
   python3 -m http.server 8000
   
   # Using Node.js
   npx serve .
   
   # Then visit: http://localhost:8000
   ```

## 🌐 Deployment Options

### Free Hosting

**GitHub Pages:**
```bash
# Create gh-pages branch and push
git checkout -b gh-pages
git add frontend/
git commit -m "Deploy frontend"
git push origin gh-pages
```

**Netlify:**
1. Drag & drop `index.html` to [netlify.com/drop](https://netlify.com/drop)
2. Get instant live URL

**Vercel:**
```bash
npx vercel --prod
```

### AWS Hosting (Recommended)

**S3 Static Website:**
```bash
# Create S3 bucket for website
aws s3 mb s3://your-translate-frontend

# Upload files
aws s3 cp index.html s3://your-translate-frontend/

# Enable static website hosting
aws s3 website s3://your-translate-frontend --index-document index.html
```

## 🔧 Configuration

The frontend is pre-configured to use your API endpoint:
```javascript
const API_ENDPOINT = 'https://tdns0znam4.execute-api.us-east-1.amazonaws.com/dev/translate';
```

To use a different API endpoint, update the `API_ENDPOINT` variable in `index.html`.

## 📱 Usage

1. **Select Languages** - Choose source and target languages from dropdowns
2. **Enter Text** - Type or paste text to translate
3. **Click Translate** - Get instant translation results
4. **View Results** - See original and translated text side by side

## 🎨 Customization

### Colors
Update the CSS variables to match your brand:
```css
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --accent-color: #667eea;
}
```

### Languages
Add more languages by updating the select options:
```html
<option value="ar">Arabic</option>
<option value="hi">Hindi</option>
```

## 🔒 Security

- **CORS Enabled** - API configured for cross-origin requests
- **Input Validation** - Client-side validation for all inputs
- **Error Handling** - Graceful handling of API errors

## 📊 Browser Support

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use in your projects!

---

**Live Demo:** [Your deployed URL here]  
**API Documentation:** [Link to API docs]  
**Backend Repository:** [Link to main project]