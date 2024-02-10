from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
# from dotenv import load_dotenv
from google.cloud import storage
import os
import google.generativeai as genai
import json
import re

# load_dotenv()
genai.configure(api_key="AIzaSyDo3bbDydm0fN9V2es__wTP_QAD7nwDXO0")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/app/app/ONDC_GCP.json"
client = storage.Client()
bucket_name = 'ondc_hackathonimage'


model = genai.GenerativeModel('gemini-pro-vision')
model2 = genai.GenerativeModel('gemini-pro')
prompt = """
    You are an e-commerce platform looking to digitize your product catalog. Your task is to extract relevant data from the given image of grocery items. Your output should be structured as follows:

{     
    "name": Name of the product,
    "description": Description of the product, highlighting its features and qualities. Ensure it reflects the Indian context - less than 40 words,
    "price": Price of the product if mentioned in the image, otherwise leave empty,
    "category": [
        Select only 1 category from the following options:,
        - Fruits & Vegetables,
        - Foodgrains, Oil & Masala,
        - Bakery, Cakes & Dairy,
        - Beverages,
        - Snacks & Branded Foods,
        - Beauty & Hygiene,
        - Cleaning & Household
    ], 
    "sub_category": [
        Select top 3 from the following options -
- Fresh Vegetables,
- Herbs & Seasonings,
- Sliced & Peeled Veggies,
- Fresh Salads & Sprouts,
- Atta, Flours & Sooji,
- Dals & Pulses,
- Dry Fruits,
- Edible Oils & Ghee,
- Masalas & Spices,
- Organic Staples,
- Rice & Rice Products,
- Salt, Sugar & Jaggery,
- Bakery Snacks,
- Breads & Buns,
- Cakes & Pastries,
- Cookies, Rusk & Khari,
- Dairy,
- Coffee,
- Energy & Soft Drinks,
- Fruit Juices & Drinks,
- Health Drink, Supplement,
- Tea,
- Water,
- Ice Creams & Desserts,
- Non Dairy,
- Biscuits & Cookies,
- Breakfast Cereals,
- Chocolates & Candies,
- Frozen Veggies & Snacks,
- Indian Mithai,
- Noodle, Pasta, Vermicelli,
- Pickles & Chutney,
- Ready To Cook & Eat,
- Snacks & Namkeen,
- Spreads, Sauces, Ketchup,
- Veg Snacks,
- Bath & Hand Wash,
- Feminine Hygiene,
- Hair Care,
- Health & Medicine,
- Makeup,
- Men's Grooming,
- Oral Care,
- Skin Care,
- All Purpose Cleaners,
- Bins & Bathroom Ware,
- Car & Shoe Care,
- Detergents & Dishwash,
- Disposables, Garbage Bag,
- Fresheners & Repellents,
- Mops, Brushes & Scrubs,
- Party & Festive Needs,
- Pooja Needs,
- Stationery],
"variants": [
        size: Mention the size of the product if mentioned in the image, otherwise leave empty and use the apt unit measurements based the product.,
        flavours: Mention the size of the product if mentioned in the image, otherwise leave empty and use apt std flavour.
    ] for variants give array inside dictionaries.
    "sku": Generate a unique SKU ID for each product using the following format - First two char of the product name + First two char of the category name + First two char of the sub category name  + 5 Growing number combination,
}
"""
def convert_variants_format(original_variants):
    reformatted_variants = []
    for variant in original_variants:
        for key, value in variant.items():
            reformatted_variants.append({key: value})
    return reformatted_variants


async def get_gemini_response(image_data):
    response = model.generate_content([ image_data[0], prompt])
    #response = json.dump(response.text)
    # print(eval(response.text.replace('json','')))
    print(response.text)
    text = response.text.replace('json','')
    print(text)
    text = eval(text.replace('`',''))
    # print(text)
    text = {
        **text,
        "variants" : convert_variants_format(text["variants"])
    }
    return text

def process_image(uploaded_file: UploadFile):
    if uploaded_file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    uploaded_file.file.seek(0)
    image_content = uploaded_file.file.read()
    #print("################################################################",image_content)
    if not image_content:
        raise HTTPException(status_code=400, detail="Empty image content")

    #image = Image.open(BytesIO(uploaded_file.file.read()))
    return  image_content


async def get_gemini_text(input_text):
    promptt = f"""
    You are an expert enabling ecommerce sellers by making it easier to digitize the catalog, from the given product details {input_text} extract the data such as product name and generate the product description based on the name extracted, select one apt category, select top 3 sub-category which will be apt and price only if mentioned, variants such as color and size only if it is mentioned and if product details does not contain enough information to extract the requested data fields. just give output no issue, don't give null else give empty string.
    name: extract from the text ,
    description :  "Generated Product Description Based on the Product Name  highlighting its features and qualities. Ensure it reflects the Indian context - less than 40 words,",
    "price": Price of the product if mentioned in the text, otherwise leave empty,
    "category": [
        Select only 1 category from the following options:,
        - Fruits & Vegetables,
        - Foodgrains, Oil & Masala,
        - Bakery, Cakes & Dairy,
        - Beverages,
        - Snacks & Branded Foods,
        - Beauty & Hygiene,
        - Cleaning & Household
    ],
    "sub_category": [
        Select top 3 from the following options -
- Fresh Vegetables,
- Herbs & Seasonings,
- Sliced & Peeled Veggies,
- Fresh Salads & Sprouts,
- Atta, Flours & Sooji,
- Dals & Pulses,
- Dry Fruits,
- Edible Oils & Ghee,
- Masalas & Spices,
- Organic Staples,
- Rice & Rice Products,
- Salt, Sugar & Jaggery,
- Bakery Snacks,
- Breads & Buns,
- Cakes & Pastries,
- Cookies, Rusk & Khari,
- Dairy,
- Coffee,
- Energy & Soft Drinks,
- Fruit Juices & Drinks,
- Health Drink, Supplement,
- Tea,
- Water,
- Ice Creams & Desserts,
- Non Dairy,
- Biscuits & Cookies,
- Breakfast Cereals,
- Chocolates & Candies,
- Frozen Veggies & Snacks,
- Indian Mithai,
- Noodle, Pasta, Vermicelli,
- Pickles & Chutney,
- Ready To Cook & Eat,
- Snacks & Namkeen,
- Spreads, Sauces, Ketchup,
- Veg Snacks,
- Bath & Hand Wash,
- Feminine Hygiene,
- Hair Care,
- Health & Medicine,
- Makeup,
- Men's Grooming,
- Oral Care,
- Skin Care,
- All Purpose Cleaners,
- Bins & Bathroom Ware,
- Car & Shoe Care,
- Detergents & Dishwash,
- Disposables, Garbage Bag,
- Fresheners & Repellents,
- Mops, Brushes & Scrubs,
- Party & Festive Needs,
- Pooja Needs,
- Stationery],
"variants": [
        size: Mention the size of the product if mentioned in the text, otherwise leave empty and use the apt unit measurements based the product.,
        flavours: Mention the size of the product if mentioned in the text, otherwise leave empty and use apt std flavour.
    ] for variants give array inside dictionaries.
    "sku": Generate a unique SKU ID for each product using the following format - First two char of the product name + First two char of the category name + First two char of the sub category name  + 5 Growing number combination,


    give output in this json format.
     """
    response = model2.generate_content(promptt)
    print(response.text)
    text = response.text.replace('json','').replace('null','""')
    print(text)
    text = eval(text.replace('`',''))
    return text

async def upload_image_to_gcs(uploaded_file: UploadFile):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(uploaded_file.filename)
    blob.upload_from_file(uploaded_file.file)
    image_url = f'https://storage.googleapis.com/{bucket_name}/{blob.name}'
    image_url = blob.public_url
    return  image_url
