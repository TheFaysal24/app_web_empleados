"""
Recipe Manager
Local recipe storage and retrieval for the cooking AI agent.
"""
import json
import os
from typing import Optional, List, Dict, Any


class RecipeManager:
    """Manage local recipe database and search."""
    
    def __init__(self, recipe_file: str = "recipes.json"):
        """
        Initialize recipe manager.
        
        Args:
            recipe_file: Path to JSON file storing recipes
        """
        self.recipe_file = recipe_file
        self.recipes = self._load_recipes()
    
    def _load_recipes(self) -> List[Dict[str, Any]]:
        """Load recipes from JSON file."""
        if os.path.exists(self.recipe_file):
            try:
                with open(self.recipe_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_recipes(self) -> None:
        """Save recipes to JSON file."""
        with open(self.recipe_file, 'w', encoding='utf-8') as f:
            json.dump(self.recipes, f, indent=2, ensure_ascii=False)
    
    def add_recipe(self, recipe: Dict[str, Any]) -> None:
        """
        Add a new recipe to the database.
        
        Args:
            recipe: Recipe dictionary with name, ingredients, instructions, etc.
        """
        if "name" not in recipe:
            raise ValueError("Recipe must have a 'name' field")
        self.recipes.append(recipe)
        self.save_recipes()
    
    def search_by_name(self, query: str) -> List[Dict[str, Any]]:
        """
        Search recipes by name (case-insensitive).
        
        Args:
            query: Search term
            
        Returns:
            List of matching recipes
        """
        query_lower = query.lower()
        return [r for r in self.recipes if query_lower in r.get("name", "").lower()]
    
    def search_by_ingredient(self, ingredient: str) -> List[Dict[str, Any]]:
        """
        Search recipes by ingredient.
        
        Args:
            ingredient: Ingredient to search for
            
        Returns:
            List of recipes containing that ingredient
        """
        ingredient_lower = ingredient.lower()
        matches = []
        for recipe in self.recipes:
            ingredients = recipe.get("ingredients", [])
            if any(ingredient_lower in ing.lower() for ing in ingredients):
                matches.append(recipe)
        return matches
    
    def get_recipe(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific recipe by name.
        
        Args:
            name: Recipe name
            
        Returns:
            Recipe dictionary or None if not found
        """
        for recipe in self.recipes:
            if recipe.get("name", "").lower() == name.lower():
                return recipe
        return None
    
    def list_all_recipes(self) -> List[str]:
        """Get names of all recipes in database."""
        return [r.get("name", "Unknown") for r in self.recipes]
