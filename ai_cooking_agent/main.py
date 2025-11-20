"""
Cooking AI Agent - Interactive Console Application
A conversational AI agent for recipe search, ingredient extraction, and cooking assistance.
Powered by GitHub-hosted AI models.
"""
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from github_models_client import GitHubModelsClient
from recipe_manager import RecipeManager

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")


class CookingAIAgent:
    """Interactive cooking AI agent."""
    
    def __init__(self):
        """Initialize the cooking AI agent."""
        try:
            self.client = GitHubModelsClient()
            print("✓ GitHub Models client initialized successfully!")
        except ValueError as e:
            print(f"✗ Error: {e}")
            print("\nTo use this app:")
            print("1. Set your GITHUB_TOKEN environment variable")
            print("2. Copy .env.example to .env and fill in your token")
            sys.exit(1)
        
        self.recipe_manager = RecipeManager()
        self.commands = {
            "search": self.cmd_search_recipe,
            "ingredients": self.cmd_extract_ingredients,
            "substitute": self.cmd_substitute_ingredient,
            "local": self.cmd_search_local,
            "list": self.cmd_list_recipes,
            "help": self.cmd_help,
            "exit": self.cmd_exit,
        }
    
    def cmd_search_recipe(self, args: str) -> None:
        """Search for recipes using AI."""
        if not args.strip():
            print("Usage: search <recipe query>")
            return
        
        print(f"\n🔍 Searching for recipes matching: '{args}'...")
        result = self.client.search_recipes(args)
        
        if "recipes" in result:
            for i, recipe in enumerate(result["recipes"], 1):
                print(f"\n📖 Recipe {i}: {recipe.get('name', 'Unknown')}")
                if "prep_time" in recipe:
                    print(f"   ⏱ Prep time: {recipe['prep_time']}")
                if "cook_time" in recipe:
                    print(f"   ⏱ Cook time: {recipe['cook_time']}")
                if "servings" in recipe:
                    print(f"   🍽 Servings: {recipe['servings']}")
                if "ingredients" in recipe:
                    print("   📋 Ingredients:")
                    for ing in recipe["ingredients"][:5]:
                        print(f"      • {ing}")
                    if len(recipe.get("ingredients", [])) > 5:
                        print(f"      ... and {len(recipe['ingredients']) - 5} more")
        else:
            print(result.get("response", "No recipes found."))
    
    def cmd_extract_ingredients(self, args: str) -> None:
        """Extract ingredients from recipe text using AI."""
        if not args.strip():
            print("Usage: ingredients <recipe text or recipe name>")
            return
        
        print(f"\n🔍 Extracting ingredients from: '{args[:50]}...'")
        result = self.client.extract_ingredients(args)
        
        if "ingredients" in result:
            print("\n📋 Extracted Ingredients:")
            for ing in result["ingredients"]:
                print(f"   • {ing}")
        
        if result.get("dietary_info"):
            print("\n🥗 Dietary Info:")
            for key, value in result["dietary_info"].items():
                print(f"   • {key}: {value}")
        
        if result.get("allergens"):
            print("\n⚠️ Allergens:")
            for allergen in result["allergens"]:
                print(f"   • {allergen}")
    
    def cmd_substitute_ingredient(self, args: str) -> None:
        """Find ingredient substitutions using AI."""
        if not args.strip():
            print("Usage: substitute <ingredient name>")
            return
        
        print(f"\n🔍 Finding substitutions for: '{args}'...")
        result = self.client.suggest_substitutions(args)
        
        print(f"\n🔄 Substitutions for {result.get('original', args)}:")
        
        if result.get("substitutions"):
            for sub in result["substitutions"]:
                if isinstance(sub, dict):
                    print(f"   • {sub.get('name', 'Unknown')}")
                    if "ratio" in sub:
                        print(f"     Ratio: {sub['ratio']}")
                    if "notes" in sub:
                        print(f"     Notes: {sub['notes']}")
                else:
                    print(f"   • {sub}")
        else:
            print("   No substitutions found.")
        
        if result.get("best_for"):
            print(f"\n💡 Best for: {result['best_for']}")
    
    def cmd_search_local(self, args: str) -> None:
        """Search local recipe database."""
        if not args.strip():
            print("Usage: local <recipe name>")
            return
        
        print(f"\n🔍 Searching local recipes for: '{args}'...")
        results = self.recipe_manager.search_by_name(args)
        
        if results:
            for recipe in results:
                print(f"\n📖 {recipe.get('name', 'Unknown')}")
                if "prep_time" in recipe:
                    print(f"   ⏱ Prep time: {recipe['prep_time']}")
                if "ingredients" in recipe:
                    print(f"   📋 Ingredients: {len(recipe['ingredients'])} items")
        else:
            print(f"   No local recipes matching '{args}'.")
    
    def cmd_list_recipes(self, args: str) -> None:
        """List all recipes in local database."""
        recipes = self.recipe_manager.list_all_recipes()
        
        if recipes:
            print("\n📚 Recipes in Database:")
            for i, name in enumerate(recipes, 1):
                print(f"   {i}. {name}")
        else:
            print("\n📚 No recipes in database yet.")
    
    def cmd_help(self, args: str) -> None:
        """Show help information."""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║           Cooking AI Agent - Command Reference                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║ SEARCH COMMANDS:                                               ║
║   search <query>      - Search for recipes (AI-powered)        ║
║   local <name>        - Search local recipe database           ║
║   list                - List all local recipes                 ║
║                                                                ║
║ INGREDIENT COMMANDS:                                           ║
║   ingredients <text>  - Extract ingredients from text (AI)     ║
║   substitute <item>   - Find ingredient substitutions (AI)     ║
║                                                                ║
║ OTHER:                                                         ║
║   help                - Show this help message                 ║
║   exit                - Exit the application                   ║
║                                                                ║
║ EXAMPLES:                                                      ║
║   > search pasta carbonara                                     ║
║   > ingredients 2 cups flour, 1 egg, 1 cup milk               ║
║   > substitute butter                                          ║
║   > local pasta                                                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
        print(help_text)
    
    def cmd_exit(self, args: str) -> None:
        """Exit the application."""
        print("\n👋 Goodbye! Happy cooking!")
        sys.exit(0)
    
    def run(self) -> None:
        """Run the interactive agent loop."""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                  🍳 Cooking AI Agent 🍳                        ║
║                                                                ║
║  Your AI-powered cooking assistant powered by GitHub Models   ║
║  Type 'help' for available commands                            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command in self.commands:
                    self.commands[command](args)
                else:
                    print(f"Unknown command: '{command}'. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point."""
    agent = CookingAIAgent()
    agent.run()


if __name__ == "__main__":
    main()
