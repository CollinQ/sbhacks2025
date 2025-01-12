import os
import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import io
import csv
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import caching
import pandas as pd
import time
from supabase import create_client, Client
import uuid
from .save_frames import save_frames


# Load environment variables from .env file
load_dotenv()

marketplace_schema = [
    {
        "field": "title",
        "type": "str",
        "required": True,
        "max_length": 150,
        "description": "Brief, descriptive title of the item. Should be clear and specific with proper capitalization.",
        "example": "Blue Facebook T-Shirt (Unisex)"
    },
    {
        "field": "price",
        "type": "int",
        "required": True,
        "description": "Whole number price in USD. Do not include currency symbols or decimal points.",
        "example": "20"
    },
    {
        "field": "condition",
        "type": "str",
        "required": True,
        "allowed_values": [
            "New",
            "Used - Like New",
            "Used - Good",
            "Used - Fair"
        ],
        "description": "Item condition using only the supported values. Must match exactly as specified. Use video details to determine condition.",
        "example": "New"
    },
    {
        "field": "description",
        "type": "str",
        "required": False,
        "max_length": 5000,
        "description": "Detailed description of the item including relevant details like size, color, material, and features. Can include formatting and special characters but do not include commas.",
        "example": "A vibrant blue crewneck T-shirt with a Facebook logo for all shapes and sizes. Made from 100% cotton."
    },
    {
        "field": "category",
        "type": "str",
        "required": False,
        "description": "Category path using forward slashes to indicate hierarchy. Each level should be properly capitalized and use the exact category names from the marketplace.",
        "example": "Clothing, Shoes & Accessories//Men's Clothing//T-Shirts"
    },
    {
        "field": "timestamp",
        "type": "str",
        "description": "Time in MM:SS format with leading zeros.",
        "example": "01:30"
    },
]

def load_prompt(filename: str) -> str:
    """Load prompt text from a file."""
    prompt_path = Path(__file__).parent / 'prompts' / filename
    with open(prompt_path, 'r') as f:
        return f.read().strip()

def setup_gemini_models(api_key: str, system_prompt: str) -> Dict[str, genai.GenerativeModel]:
    """Setup and return Gemini models with configuration."""
    # Configure the API key
    genai.configure(api_key=api_key)

    # Create the model config
    generation_config = {
        "temperature": 0.2,  # default is 0.2
        "top_p": 0.95,      # default is 0.95
        "top_k": 40,        # default is 40
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    # Setup models
    models = {
        'flash_8b': genai.GenerativeModel(
            model_name="models/gemini-1.5-flash-8b",
            system_instruction=system_prompt,
            generation_config=generation_config
        ),
        'flash': genai.GenerativeModel(
            model_name="models/gemini-1.5-flash-002",
            system_instruction=system_prompt,
            generation_config=generation_config
        ),
        'pro': genai.GenerativeModel(
            model_name="models/gemini-1.5-pro-002",
            system_instruction=system_prompt,
            generation_config=generation_config
        )
    }
    
    return models

def generate_content(prompt: str, model: genai.GenerativeModel):
    """Returns a given model's output for a given prompt."""
    return model.generate_content(prompt)


def setup_video_cache(video_file_upload, system_prompt: str, cache_minutes: int = 15) -> Optional[caching.CachedContent]:
    """Setup and return video content cache."""
    try:
        video_file_cache = caching.CachedContent.get(name="cachedContents/db8qp5uvbw27")
    except Exception:
        video_file_cache = None

    if video_file_cache is None:
        video_file_cache = caching.CachedContent.create(
            model="models/gemini-1.5-flash-002",
            display_name="house item catalogue video",
            system_instruction=system_prompt,
            contents=[video_file_upload],
            ttl=datetime.timedelta(minutes=cache_minutes)
        )
    
    return video_file_cache

def get_field_names_as_list() -> List[str]:
    """Returns the expected field names for the marketplace schema."""
    return ["title", "price", "condition", "description", "category", "timestamp"]

def quick_check_marketplace_csv(model_output,
                              ideal_number_of_fields: Optional[int] = len(get_field_names_as_list()),
                              target_start_tag: str = "<csv>",
                              target_end_tag: str = "</csv>") -> tuple[str, bool, List[str]]:
    """
    Extracts and validates a marketplace CSV from a model's output and performs formatting checks.
    """
    # Get text output from model
    output_text = model_output.text

    # Verify tags exist
    assert target_start_tag in output_text, f"target_start_tag: {target_start_tag} not in model's output text"
    assert target_end_tag in output_text, f"target_end_tag: {target_end_tag} not in model's output text"

    # Clean up the text
    output_text = output_text.replace("```csv", "").replace("```", "")

    # Extract CSV string from tags
    csv_string = output_text.split(target_start_tag)[1].split(target_end_tag)[0].strip()

    # Setup CSV handling
    input_csv = io.StringIO(csv_string)
    output_csv = io.StringIO()
    reader = csv.reader(input_csv)
    writer = csv.writer(output_csv)

    # Track validation issues
    field_counts = []
    fixes_required = []
    fix_csv_required = False

    print(f"[INFO] Ideal number of fields: {ideal_number_of_fields}")

    # Process each row
    for i, row in enumerate(reader):
        # For first row, set ideal number if not provided
        if ideal_number_of_fields is None and i == 0:
            ideal_number_of_fields = len(row)
            print(f"[INFO] Ideal number of fields: {ideal_number_of_fields}")

        # Validate field count
        field_counts.append(len(row))
        if len(row) != ideal_number_of_fields:
            error_string = f"[INFO] Row {i} has an unexpected number of fields: {len(row)} (expected: {ideal_number_of_fields})"
            print(error_string)
            fixes_required.append(f"Error: {error_string.replace('[INFO] ', '')} | Row to fix: {','.join(row)}")
            fix_csv_required = True

        # Additional marketplace-specific validations
        if i > 0:  # Skip header row
            try:
                # Validate price is a whole number
                if row[1]:  # price field
                    int(row[1])

                # Validate condition is one of allowed values
                valid_conditions = ["New", "Used - Like New", "Used - Good", "Used - Fair"]
                if row[2] and row[2] not in valid_conditions:
                    error_string = f"[INFO] Row {i} has invalid condition: {row[2]}"
                    print(error_string)
                    fixes_required.append(f"Error: Invalid condition in row {i}")
                    fix_csv_required = True

                # Validate title length
                if len(row[0]) > 150:
                    error_string = f"[INFO] Row {i} title exceeds 150 characters"
                    print(error_string)
                    fixes_required.append(f"Error: Title too long in row {i}")
                    fix_csv_required = True

                # Validate description length
                if row[3] and len(row[3]) > 5000:
                    error_string = f"[INFO] Row {i} description exceeds 5000 characters"
                    print(error_string)
                    fixes_required.append(f"Error: Description too long in row {i}")
                    fix_csv_required = True

            except ValueError:
                error_string = f"[INFO] Row {i} has invalid price format"
                print(error_string)
                fixes_required.append(f"Error: Invalid price in row {i}")
                fix_csv_required = True

        # Fix problematic fields
        fixed_row = [
            f'"{field}"'.replace('"""', '"') if any(char in field for char in [",", "\n", '"']) else field
            for field in row
        ]

        writer.writerow(fixed_row)

    # Get the fixed CSV content
    output_csv.seek(0)
    output_csv_extracted = output_csv.getvalue()

    # Print summary
    if fix_csv_required:
        print("[INFO] Some rows required fixing.")
    else:
        print("[INFO] No issues detected in the CSV.")

    return output_csv_extracted, fix_csv_required, fixes_required

def get_schema_string() -> str:
  """Returns a simple string representation of the schema."""
  return "\n".join([
      f"{i+1}. {field['field']} ({field['type']}): {field['description']} Example: {field['example']}"
      for i, field in enumerate(marketplace_schema)
  ])

def fix_csv(input_csv, fixes_required, model):
    """Takes in a broken CSV specific to our marketplace listing schema and uses Gemini to fix it."""
    fix_csv_prompt = load_prompt('fix_csv_prompt.txt')
    model_input_prompt = fix_csv_prompt.format(input_csv=input_csv, fixes_required=fixes_required)
    return generate_content(prompt=model_input_prompt, model=model)

def upload_items_to_supabase(df: pd.DataFrame, user_id: str) -> List[str]:
    """Upload items to Supabase and return list of item IDs."""
    # Setup Supabase client
    url: str = os.environ.get("SUPABASE_PROJECT_URL")
    key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)
    
    item_ids = []
    
    # Process each row and upload to Supabase
    for _, row in df.iterrows():
        item_data = {
            "id": row['id'],
            "user_id": user_id,
            "title": row['title'],
            "description": row['description'],
            "price": int(row['price']),  # Convert to numeric
            "condition": row['condition'],
            "status": "unlisted",  # Default status
            "image_url": row['image_url'],  # Can be updated later
            "category": "Miscellaneous",
        }
        
        # Synchronous insert
        response = supabase.table("items").insert(item_data).execute()
        
        # Verify successful insertion
        if response.data:
            item_ids.append(response.data[0]['id'])
    
    return item_ids

def main(path_to_video_file):
    # Load prompts
    system_prompt = load_prompt('system_prompt.txt')
    example_1 = load_prompt('example_1.txt')
    example_2 = load_prompt('example_2.txt')
    example_3 = load_prompt('example_3.txt')
    example_4 = load_prompt('example_4.txt')
    initial_prompt = load_prompt('initial_prompt.txt')

    input_prompt_initial = initial_prompt.format(
        csv_input_schema=get_schema_string(),
        example_1=example_1,
        example_2=example_2,
        example_3=example_3,
        example_4=example_4
    )
    
    # Setup models
    models = setup_gemini_models(os.getenv('GEMINI_API_KEY'), system_prompt)
    model = models['flash']  # Choose which model to use
    
    # Process video and get initial response
    video_file_upload = genai.upload_file(path=path_to_video_file)
    while video_file_upload.state.name == "PROCESSING":
        print(".", end="")
        time.sleep(2)
        video_file_upload = genai.get_file(video_file_upload.name)
    if video_file_upload.state.name == "FAILED":
        print(f"[ERROR] Video file upload failed")
        print(f"[ERROR] State: {video_file_upload.state.name}")
        print(f"[ERROR] Error: {video_file_upload.error}")
        raise ValueError(video_file_upload.state.name)
    
    print(f"[INFO] Video file uploaded: {video_file_upload.name}")
    print(f"[INFO] Video file state: {video_file_upload.state.name}")
    
    start_time = time.time()
    model_response_1 = generate_content(
        prompt=[video_file_upload, input_prompt_initial],
        model=model
    )
    end_time = time.time()
    print(f"[INFO] Time taken for model_response_1: {round(end_time - start_time, 2)} seconds")
    print(model_response_1.text)
    
    # Validate and fix CSV if needed
    model_response_1_csv, fix_csv_1_required, csv_fixes_to_do_1 = quick_check_marketplace_csv(
        model_output=model_response_1,
        target_start_tag="<csv>",
        target_end_tag="</csv>"
    )
    
    print(f"[INFO] CSV fix required? {fix_csv_1_required}")
    print(f"[INFO] Fixes to do:\n{csv_fixes_to_do_1}")
    
    while fix_csv_1_required:
        print(f"[INFO] CSV fix required... fixing...")
        model_response_1_csv = fix_csv(
            input_csv=model_response_1_csv,
            fixes_required=csv_fixes_to_do_1,
            model=model
        )
        print(model_response_1_csv)
        model_response_1_csv, fix_csv_1_required, csv_fixes_to_do_1 = quick_check_marketplace_csv(
            model_output=model_response_1_csv
        )
        print(f"[INFO] CSV fix required? {fix_csv_1_required}")
        print(f"[INFO] Fixes to do:\n{csv_fixes_to_do_1}")

        print(model_response_1_csv[:1000])

    # Read CSV with correct column names and skip the first row (which is headers)
    df_1 = pd.read_csv(
        io.StringIO(model_response_1_csv), 
        names=['title', 'price', 'condition', 'description', 'category', 'timestamp'],
        skiprows=1,  # Skip the header row from the CSV
        on_bad_lines="warn"
    )
    df_final_json = []
    print("[DEBUG] DataFrame head:", df_1.head())
    for idx, row in df_1.iterrows():
        item = {
            "id": str(uuid.uuid4()),
            "item_number": idx + 1,  # 1-based indexing
            "title": row['title'],
            "price": row['price'],
            "condition": row['condition'],
            "description": row['description'],
            "category": row['category'],
            "timestamp": row['timestamp']
        }
        df_final_json.append(item)
    image_urls = save_frames(df_final_json, path_to_video_file)
    
    # Alternative DataFrame approach
    df_final = pd.DataFrame(df_final_json)
    df_final['image_url'] = image_urls
    item_ids = upload_items_to_supabase(df_final, "d69d4ed1-734b-4c40-8ac6-3b641784505e")
    print(f"[INFO] Successfully uploaded {len(item_ids)} items")
    print(f"[INFO] Item IDs: {item_ids}")
    return item_ids

if __name__ == "__main__":
    print("[INFO] Starting script...")
    video_file = input("Please enter the path to your video file: ")
    path_to_video_file = process.env.NEXT_PUBLIC_API_BASE_URL + video_file
    print(f"[INFO] Path to video file: {path_to_video_file}")
    
    main(path_to_video_file=path_to_video_file)
