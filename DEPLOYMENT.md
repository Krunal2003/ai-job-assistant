# Deployment Guide - AI-Powered Job Application Assistant

This guide will help you deploy your Streamlit application to Streamlit Community Cloud.

## Prerequisites

- GitHub account
- OpenAI API key
- Git installed on your computer

## Step 1: Prepare Your Repository

### 1.1 Initialize Git Repository (if not already done)

```bash
cd "/Users/krunal/Desktop/AI-Powered Job Application Assistant copy/job-assistant"
git init
```

### 1.2 Add Files to Git

```bash
git add .
git commit -m "Initial commit - AI Job Application Assistant"
```

### 1.3 Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right and select "New repository"
3. Name your repository (e.g., `ai-job-assistant`)
4. Choose "Public" or "Private" (both work with Streamlit Cloud)
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### 1.4 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name.

## Step 2: Deploy to Streamlit Community Cloud

### 2.1 Sign Up for Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign up" and sign in with your GitHub account
3. Authorize Streamlit to access your GitHub repositories

### 2.2 Deploy Your App

1. Click "New app" button
2. Select your repository from the dropdown
3. Choose the branch: `main`
4. Set the main file path: `app.py`
5. Click "Deploy!"

### 2.3 Configure Secrets (IMPORTANT!)

Your app needs the OpenAI API key to work. Set it up as a secret:

1. In your deployed app dashboard, click the "⋮" menu (three dots)
2. Select "Settings"
3. Go to the "Secrets" section
4. Add your secret in TOML format:

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

5. Click "Save"
6. Your app will automatically restart with the new secret

## Step 3: Test Your Deployed App

Once deployed, test all features:

1. **Upload Documents**: Upload your resume/portfolio files
2. **Process Documents**: Click "Process and Index Documents"
3. **Generate Materials**: 
   - Enter job description
   - Generate resume bullets
   - Generate cover letter
   - Check ATS analysis
   - Generate LinkedIn message
4. **Theme Toggle**: Test dark/light mode switching
5. **Download**: Test downloading generated materials

## Troubleshooting

### App Won't Start

**Issue**: App shows error on startup

**Solutions**:
- Check that `OPENAI_API_KEY` is set in Secrets
- Verify all dependencies in `requirements.txt` are compatible
- Check Streamlit Cloud logs for specific error messages

### "Module Not Found" Errors

**Issue**: Import errors for custom modules

**Solutions**:
- Ensure all files are committed to GitHub
- Check that the `src/` directory structure is intact
- Verify file paths are relative, not absolute

### ChromaDB/Vector Store Issues

**Issue**: Document indexing fails

**Solutions**:
- The `data/` directory is excluded by `.gitignore` (this is correct)
- Vector store is created fresh on each deployment
- Users need to re-upload documents after each deployment

### API Key Not Working

**Issue**: OpenAI API errors

**Solutions**:
- Verify API key is valid at [OpenAI Platform](https://platform.openai.com/api-keys)
- Check that the key has sufficient credits
- Ensure the secret is formatted correctly in Streamlit Cloud (no quotes around the key value)

### Slow Performance

**Issue**: App is slow or times out

**Solutions**:
- Streamlit Community Cloud has resource limits
- Large document processing may take time
- Consider upgrading to Streamlit Cloud paid tier for better performance

## Updating Your Deployed App

To update your deployed app:

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
3. Streamlit Cloud will automatically detect changes and redeploy

## App URL

After deployment, your app will be available at:
```
https://YOUR_USERNAME-YOUR_REPO_NAME-BRANCH-app-HASH.streamlit.app
```

You can customize this URL in the Streamlit Cloud settings.

## Important Notes

- **Free Tier Limits**: Streamlit Community Cloud free tier has resource limits
- **Data Persistence**: Uploaded documents are NOT persisted between deployments
- **API Costs**: OpenAI API usage incurs costs based on your usage
- **Privacy**: Your code is public if you use a public GitHub repository

## Support

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Community Forum](https://discuss.streamlit.io)
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)

---

**Congratulations!** Your AI-Powered Job Application Assistant is now deployed and accessible from anywhere! 🎉
