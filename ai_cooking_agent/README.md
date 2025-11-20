# Cooking AI Agent

A conversational AI agent for recipe search, ingredient extraction, and cooking assistance using GitHub-hosted language models.

## Features

- **🔍 AI-Powered Recipe Search** - Find recipes with natural language queries
- **📋 Ingredient Extraction** - Automatically extract ingredients and dietary info from recipe text
- **🔄 Ingredient Substitutions** - Get suggestions for ingredient substitutions (allergies, preferences, etc.)
- **📚 Local Recipe Database** - Store and search your own recipes
- **💬 Interactive Console** - User-friendly command-line interface

## Setup

### Prerequisites

- Python 3.8+
- GitHub account with access to GitHub Models API
- GitHub Personal Access Token (PAT)

### Installation

1. **Clone or navigate to the project:**
   ```bash
   cd ai_cooking_agent
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your GitHub token:
   ```
   GITHUB_TOKEN=your_github_pat_here
   GITHUB_MODEL=gpt-4o-mini
   ```

   To get a GitHub token:
   - Visit https://github.com/settings/tokens
   - Create a new PAT with `read:user` scope
   - Or use GitHub Models API tokens from https://github.com/marketplace/models

## Usage

### Run the Agent

```bash
python main.py
```

### Commands

#### Recipe Search (AI-Powered)
```
> search pasta carbonara
```
Searches for recipes using the GitHub AI model.

#### Extract Ingredients (AI-Powered)
```
> ingredients 2 cups flour, 1 egg, 1 cup milk, sugar
```
Extracts structured ingredient data from recipe text using AI.

#### Find Substitutions (AI-Powered)
```
> substitute butter
```
Get ingredient substitution suggestions.

#### Search Local Database
```
> local pasta
```
Search your local recipe database by name.

#### List All Local Recipes
```
> list
```
Show all recipes stored locally.

#### Help
```
> help
```
Display available commands.

#### Exit
```
> exit
```
Close the application.

## Architecture

### Modules

- **`main.py`** - Interactive console application and agent orchestration
- **`github_models_client.py`** - GitHub Models API client with recipe/ingredient methods
- **`recipe_manager.py`** - Local recipe storage and retrieval
- **`recipes.json`** - Sample recipe database (add your own recipes here)

### GitHub Models API

This app uses the GitHub Models API to call language models. Supported models:
- `gpt-4o-mini` (default, free tier)
- `gpt-4o`
- `gpt-4-turbo`
- `claude-3.5-sonnet`

Configure the model in `.env` via `GITHUB_MODEL` variable.

## Example Session

```
╔════════════════════════════════════════════════════════════════╗
║                  🍳 Cooking AI Agent 🍳                        ║
║                                                                ║
║  Your AI-powered cooking assistant powered by GitHub Models   ║
║  Type 'help' for available commands                            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

> search quick weeknight dinner with chicken
🔍 Searching for recipes matching: 'quick weeknight dinner with chicken'...

📖 Recipe 1: Lemon Garlic Chicken Pasta
   ⏱ Prep time: 15 minutes
   ⏱ Cook time: 20 minutes
   🍽 Servings: 4
   📋 Ingredients:
      • 500g pasta
      • 600g chicken breast, cubed
      • 4 cloves garlic, minced
      ... and 5 more

> ingredients 2 cups flour, 1 egg, 1 cup milk, salt, sugar
🔍 Extracting ingredients from: '2 cups flour, 1 egg, 1 cup milk, salt...'

📋 Extracted Ingredients:
   • 2 cups flour
   • 1 egg
   • 1 cup milk
   • salt
   • sugar

> exit
👋 Goodbye! Happy cooking!
```

## Configuration

### Environment Variables

- `GITHUB_TOKEN` (required) - Your GitHub Personal Access Token
- `GITHUB_MODEL` (optional, default: `gpt-4o-mini`) - Which GitHub Model to use

### Adding Custom Recipes

Edit `recipes.json` or use the app to add recipes:

```json
{
  "name": "Your Recipe Name",
  "prep_time": "15 minutes",
  "cook_time": "30 minutes",
  "servings": 4,
  "ingredients": ["ingredient 1", "ingredient 2"],
  "instructions": "Step by step instructions..."
}
```

## Troubleshooting

### "GITHUB_TOKEN not set" Error

Make sure you have:
1. Created a `.env` file from `.env.example`
2. Added your GitHub token to the `.env` file
3. Or set the `GITHUB_TOKEN` environment variable directly

### API Rate Limits

GitHub Models API has rate limits. Free tier allows a reasonable number of requests. If you hit limits, wait before making more requests.

### Model Response Issues

If the model returns invalid JSON:
- The app has fallback parsing to extract useful data
- Try rephrasing your query
- Check your internet connection

## Best Practices for GitHub Models

This app follows the best practices from the Microsoft Agent Framework:

- **Model Selection**: Uses `gpt-4o-mini` by default (free tier, excellent performance)
- **Error Handling**: Graceful fallbacks for API failures
- **Configuration**: Environment-based config for security
- **Prompting**: Clear system prompts for consistent, structured responses

## License

MIT License - See LICENSE file for details.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your GitHub token has the correct permissions
3. Review GitHub Models documentation: https://github.com/marketplace/models

---

**Happy cooking! 🍳**
