# GitHub Models API - Alternative Model Names

If you're still getting access errors, try these alternative model names in your `backend/config/config.py`:

## Option 1: Try different GPT-4 variants
```python
DEFAULT_MODEL = 'gpt-4o-mini'  # Current setting
DEFAULT_MODEL = 'gpt-4o'       # Without openai/ prefix
DEFAULT_MODEL = 'gpt-4'        # Standard GPT-4
```

## Option 2: Try other available models
```python
DEFAULT_MODEL = 'gpt-3.5-turbo'
DEFAULT_MODEL = 'claude-3-haiku'
DEFAULT_MODEL = 'claude-3-sonnet'
```

## How to test which models you have access to:

You can make a test API call to see available models:

```bash
curl -H "Authorization: Bearer YOUR_GITHUB_PAT" \
     -H "X-GitHub-Api-Version: 2022-11-28" \
     https://api.github.com/models
```

## Quick Fix Steps:

1. Edit `backend/config/config.py`
2. Change `DEFAULT_MODEL = 'gpt-4o-mini'` to one of the alternatives above
3. Restart the backend container: `docker-compose restart backend`
4. Test the API again

## Check your GitHub Models access:

Visit https://github.com/settings/personal-access-tokens/tokens and ensure your token has:
- Models API access enabled
- Proper scopes selected