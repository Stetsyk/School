unset ANTHROPIC_BASE_URL
unset ANTHROPIC_AUTH_TOKEN
unset ANTHROPIC_API_KEY 

npm uninstall -g @anthropic-ai/claude-code
rm -rf ~/.claude ~/.claude.json ~/.claude.json.backup
npm install -g @anthropic-ai/claude-code