import os
import subprocess
from fastapi import FastAPI
from pydantic import BaseModel
import json
import re
from typing import Optional
import uvicorn

# Create the FastAPI app instance
app = FastAPI()

# Define a request model for the input (food description)
class FoodDescription(BaseModel):
    text: str

# Define a response model to structure the output (nutrition data)
class NutritionData(BaseModel):
    item: str
    calories: int
    protein: int
    carb: int
    fat: int
    error: Optional[str] = None

# Root route for the application
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Example endpoint that accepts food description and returns nutritional data
@app.post("/food-analysis", response_model=NutritionData)
async def analyze_food(food: FoodDescription):
    # Call the Ollama Mistral model with the food text as a prompt
    result = run_ollama_model(food.text)
    return result

def run_ollama_model(food_text: str) -> dict:
    # Construct the prompt to send to Ollama
    prompt = f"Estimate the total calories, protein, carb, and fat in this food description: '{food_text}'. Respond ONLY in JSON format with the following fields: calories (should be kcal value), protein (should be grams), carb (should be grams), and fat (should be grams), as numbers (without suffix such as gr). If the input seems related to food, but lacks specific details (like the type of ingredients, portion size, or exact items), make your best guess based on common serving sizes and general nutritional knowledge. Only return an error if the input is clearly unrelated to food or a meal."

    command = f"ollama run mistral \"{prompt}\""
    
    try:
        # Run the command and capture the output
        output = subprocess.check_output(command, shell=True, text=True)

        # Debug: Print raw output from Ollama
        print("Ollama Output:", output)

        # Parse the output into JSON
        response = parse_ollama_output(output)
        return response

    except subprocess.CalledProcessError as e:
        # Handle error in case Ollama fails
        return {"error": f"Error processing the input: {str(e)}"}

def parse_ollama_output(output: str) -> dict:
    try:
        # Extract the JSON portion of the output using regular expressions
        json_part = re.search(r'(\{.*\})', output, re.DOTALL)
        
        if not json_part:
            return {
                "item": "N/A",
                "calories": 0,
                "protein": 0,
                "carb": 0,
                "fat": 0,
                "error": "Sorry, I couldn't understand that. Could you please provide a clearer food description?"
            }

        # Now, try to parse the JSON part
        output_json = json.loads(json_part.group(1))

        # Check if the response seems relevant (if it contains food-related fields)
        if not output_json.get("calories") or not output_json.get("protein"):
            return {
                "item": "N/A",
                "calories": 0,
                "protein": 0,
                "carb": 0,
                "fat": 0,
                "error": "Hmm, that doesn't seem like food. Could you try describing a food item more clearly?"
            }

        # Helper function to convert strings like '60g' to integer 60
        def convert_to_int(value):
            if isinstance(value, str):
                # Remove any non-numeric characters and try to convert to integer
                value = ''.join(filter(str.isdigit, value))
                return int(value) if value else 0
            return int(value)

        # Return a standardized format with integer fields
        return {
            "item": output_json.get("item", "Unknown").lower(),  # Always include item name, even if it's unknown
            "calories": convert_to_int(output_json.get("calories", "0")),
            "protein": convert_to_int(output_json.get("protein", "0")),
            "carb": convert_to_int(output_json.get("carb", "0")),
            "fat": convert_to_int(output_json.get("fat", "0"))
        }

    except json.JSONDecodeError:
        # If parsing JSON fails, return a friendly error
        return { 
            "item": "N/A",
            "calories": 0,
            "protein": 0,
            "carb": 0,
            "fat": 0,
            "error": "Sorry, I couldn't understand that. Could you please clarify?"
        }

# Ensure the app binds to Heroku's dynamic port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)