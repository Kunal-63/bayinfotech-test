# Frontend Deployment Guide

## Platform: Vercel

The frontend is deployed on [Vercel](https://vercel.com) for optimal React/Vite performance.

**Live URL**: `http://bayinfotech-test-r9bncip32-kunal63s-projects.vercel.app`

---

## Prerequisites

1. Vercel account
2. GitHub repository connected to Vercel
3. Backend API deployed and accessible

---

## Initial Deployment

### 1. Connect Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repository: `Kunal-63/bayinfotech-test`
4. Select the repository

### 2. Configure Project

**Framework Preset**: Vite

**Root Directory**: `dsai-help-desk-main`

**Build Settings**:
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### 3. Environment Variables

Add the following environment variables:

```bash
VITE_API_BASE_URL=https://bayinfotech-test.onrender.com
VITE_API_TIMEOUT=30000
```

**How to add**:
1. Go to Project Settings → Environment Variables
2. Add each variable
3. Select all environments (Production, Preview, Development)

### 4. Deploy

Click **Deploy**. Vercel will:
1. Clone your repository
2. Install dependencies (`npm install`)
3. Build the project (`npm run build`)
4. Deploy to CDN
5. Assign a public URL

---

## Build Configuration

### vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'mui-vendor': ['@mui/material', '@mui/icons-material']
        }
      }
    }
  }
})
```

---

## Environment Configuration

### Local Development

Create `.env` file:
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

### Production

Environment variables are set in Vercel Dashboard.

**Access in code**:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
```

---

## Deployment Workflow

### Automatic Deployments

Vercel automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Vercel will:
1. Detect the push
2. Build the new version
3. Deploy to production
4. Update the live URL

### Preview Deployments

Every pull request gets a preview deployment:
- Unique URL for testing
- Isolated from production
- Automatic cleanup after merge

### Manual Deployments

From Vercel Dashboard:
1. Go to your project
2. Click **Deployments** tab
3. Click **Redeploy** on any deployment

---

## Custom Domain (Optional)

### Add Custom Domain

1. Go to Project Settings → Domains
2. Add your domain (e.g., `helpdesk.yourdomain.com`)
3. Configure DNS:
   - **Type**: CNAME
   - **Name**: helpdesk
   - **Value**: cname.vercel-dns.com

4. Wait for DNS propagation (5-60 minutes)
5. Vercel automatically provisions SSL certificate

---

## Performance Optimization

### 1. Code Splitting

Vite automatically splits code by routes:
```javascript
const TicketDashboard = lazy(() => import('./pages/TicketDashboard'))
```

### 2. Asset Optimization

Vercel automatically:
- Compresses images
- Minifies JS/CSS
- Enables Brotli compression
- Serves from global CDN

### 3. Caching

Configure cache headers in `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### 4. Bundle Analysis

```bash
npm run build -- --mode analyze
```

---

## Monitoring

### Vercel Analytics

Enable in Project Settings → Analytics:
- Page views
- Unique visitors
- Top pages
- Geographic distribution
- Device breakdown

### Web Vitals

Vercel tracks Core Web Vitals:
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

### Error Tracking

Integrate Sentry:
```bash
npm install @sentry/react
```

```javascript
import * as Sentry from "@sentry/react"

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: import.meta.env.MODE
})
```

---

## Troubleshooting

### Build Fails

**Error**: `Module not found`

**Solution**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Environment Variables Not Working

**Error**: `undefined` when accessing `import.meta.env.VITE_*`

**Solution**:
- Ensure variables start with `VITE_`
- Redeploy after adding variables
- Check variable is set in correct environment

### CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
- Verify backend CORS settings include your Vercel URL
- Check `VITE_API_BASE_URL` is correct
- Ensure backend is deployed and accessible

### Slow Build Times

**Solution**:
- Enable caching in Vercel settings
- Reduce bundle size (code splitting)
- Use `npm ci` instead of `npm install`

---

## Rollback

### Instant Rollback

1. Go to Deployments tab
2. Find the working deployment
3. Click **⋯** → **Promote to Production**

### Git Rollback

```bash
git revert HEAD
git push origin main
```

---

## CI/CD Integration

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

---

## Security

### HTTPS

- Vercel enforces HTTPS by default
- Automatic SSL certificate renewal
- HTTP → HTTPS redirect enabled

### Environment Variables

- Never commit `.env` to Git
- Use Vercel Dashboard for production secrets
- Rotate API keys regularly

### Content Security Policy

Add to `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://bayinfotech-test.onrender.com"
        }
      ]
    }
  ]
}
```

---

## Cost

### Vercel Pricing

- **Hobby (Free)**:
  - 100 GB bandwidth/month
  - Unlimited deployments
  - Automatic HTTPS
  - Perfect for this project

- **Pro ($20/month)**:
  - 1 TB bandwidth
  - Advanced analytics
  - Team collaboration

---

## Backup & Recovery

### Git-Based Backup

Every deployment is a Git commit:
```bash
# View deployment history
vercel ls

# Rollback to specific deployment
vercel rollback <deployment-url>
```

### Manual Backup

```bash
# Download production build
vercel pull
```

---

## Testing Before Deploy

### Local Build Test

```bash
npm run build
npm run preview
```

Visit `http://localhost:4173` to test production build locally.

### Lighthouse Audit

```bash
npm install -g lighthouse
lighthouse http://localhost:4173 --view
```

Target scores:
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 95
- SEO: > 90

---

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Vite Docs**: https://vitejs.dev
- **React Docs**: https://react.dev

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Backend API accessible
- [ ] CORS configured correctly
- [ ] Build succeeds locally
- [ ] No console errors
- [ ] Responsive on mobile
- [ ] Lighthouse score > 90
- [ ] Analytics enabled
- [ ] Error tracking configured
- [ ] Custom domain configured (optional)
