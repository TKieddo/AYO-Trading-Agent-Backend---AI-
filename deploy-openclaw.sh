#!/bin/bash
# Deploy OpenClaw Gateway to Railway for 24/7 operation

echo "🚀 Deploying OpenClaw Gateway to Railway..."

# 1. Create new Railway project
echo "Creating Railway project..."
railway init --name openclaw-gateway

# 2. Set environment variables
echo "Setting environment variables..."
railway variables set \
  NODE_ENV=production \
  OPENCLAW_MODE=remote \
  OPENCLAW_TOKEN=1044c265b0d10df74170c2bcd292ac239fd5035820b292f6

# 3. Copy config files
cp railway-openclaw.toml railway.toml
cp openclaw-railway.json openclaw.json

# 4. Create package.json for Railway
cat > package.json << 'EOF'
{
  "name": "openclaw-gateway",
  "version": "1.0.0",
  "scripts": {
    "start": "npx openclaw gateway start"
  },
  "dependencies": {
    "openclaw": "latest"
  }
}
EOF

# 5. Deploy
git add railway.toml openclaw.json package.json
git commit -m "Add OpenClaw gateway for 24/7 operation"
git push origin main

railway up

echo "✅ OpenClaw Gateway deployed!"
echo "📱 You'll now get WhatsApp alerts 24/7"
echo "🔗 Gateway URL: $(railway domain)"
