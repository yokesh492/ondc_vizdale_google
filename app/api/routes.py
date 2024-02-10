from fastapi import APIRouter, Depends, HTTPException, Query,File, UploadFile
from sqlalchemy.orm import Session
from app.api import schemas
from app.api import auth, crud, deps, models
from app.api.utils import process_image, get_gemini_response , get_gemini_text, upload_image_to_gcs, convert_variants_format
from fastapi.responses import JSONResponse
import json
import ast
import logging
from typing import List
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register")
async def register(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@router.post("/login")
async def login(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"user_id": db_user.id, "message": "Login successful"}



@router.post("/process_image/")
async def process_image_endpoint(
    uploaded_file: UploadFile = File(...)
):
    try:
        image_url =await upload_image_to_gcs(uploaded_file)
        print(image_url)
        image_content = process_image(uploaded_file)
        logger.info(f"Processed image content: {image_content}")
        image_data = [{"mime_type": uploaded_file.content_type, "data": image_content}]

        #print(image_data)
        gemini_response = await get_gemini_response(image_data)
        gemini_response['image'] = image_url
        return JSONResponse(content=gemini_response)#content={"response": gemini_response}
        #return gemini_response
    except FileNotFoundError as e:
        logger.exception("FileNotFoundError occurred while processing the image")
        raise HTTPException(status_code=404, detail=str(e))
    
    
@router.post("/text_catalog/")
async def get_text_catalog(input_data: schemas.InputData):
    response = await get_gemini_text(input_data.input)
    return JSONResponse(content=response)

@router.post("/add_to_catalog/{user_id}")
def create_catalogue_item(user_id: int, item: schemas.ProductCatalogCreate, db: Session = Depends(deps.get_db)):
    if item.pid == 0:
        product = crud.create_product(db=db, item=item,user_id=user_id)
        item.pid = product.id
    catalog_entry = crud.create_catalog(db=db, item=item, user_id=user_id)
    return catalog_entry

@router.get("/catalogue/{user_id}", response_model=List[schemas.ProductCatalogResponse])
def get_user_catalogue(user_id: int, db: Session = Depends(deps.get_db)):
    products = crud.get_products_by_user_id(db, user_id=user_id)
    print(products)
    if not products:
        return JSONResponse(status_code=200, content={"message": "No products found for the user. Please add a catalog."})
    
    catalogue_data = []
    for product in products:
        catalog_items = crud.get_catalog_by_product_id(db, product_id=product.id)
        product_details = schemas.ProductDetail(**product.__dict__)
        
        catalog_details_list = []  # Prepare a list to hold CatalogDetail instances or dictionaries
        for catalog_item in catalog_items:
            # Ensure variants is in the correct format
            variants = catalog_item.variants
            print(variants)
            if isinstance(variants, str):
                # Deserialize if variants is a JSON string
                variants = json.loads(variants)
            # Create a dictionary for CatalogDetail instantiation
            variants = convert_variants_format(variants)
            catalog_details_data = {
                "catalogid" : catalog_item.id,
                "inv": catalog_item.inv,
                "price": catalog_item.price,
                "discount_price": catalog_item.discount_price,
                "variants": variants
            }
            print(variants)
            # Instantiate CatalogDetail or directly append the dictionary if Pydantic can handle it
            catalog_details = schemas.CatalogDetail(**catalog_details_data)
            catalog_details_list.append(catalog_details)

        # Instantiate ProductCatalogResponse with the list of CatalogDetail instances/dictionaries
        product_catalog_response = schemas.ProductCatalogResponse(
            product=product_details,
            catalog=catalog_details_list  # Make sure this matches the expected field name in ProductCatalogResponse
        )
        catalogue_data.append(product_catalog_response)
    
    return catalogue_data

@router.get("/products/{product_id}", response_model=schemas.ProductDetail)
def get_product_detail(product_id: int, db: Session = Depends(deps.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/catalog_detail/{catalog_id}", response_model=schemas.ProductCatalogDetail)
def get_product_catalog_detail(catalog_id: int, db: Session = Depends(deps.get_db)):
    catalog = crud.get_catalog_by_id(db, catalog_id=catalog_id)
    if not catalog:
        raise HTTPException(status_code=404, detail="Catalog not found")
    product = crud.get_product_by_id(db, product_id=catalog.pid)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found associated with the catalog")
    variants = catalog.variants
    if isinstance(variants, str):
        variants = json.loads(variants)
    variants = convert_variants_format(variants)
    catalog_details_data = {
        "catalogid" : catalog.id,
        "inv": catalog.inv,
        "price": catalog.price,
        "discount_price": catalog.discount_price,
        "variants": variants
    }

    return {"catalog": catalog_details_data, "product": product}

@router.post("/create_catalog/{user_id}")
def create_catalogue_item(user_id: int, item: schemas.ProductCatalogCreate, db: Session = Depends(deps.get_db)):
    catalog_entry = crud.create_catalog(db=db, item=item, user_id=user_id)
    return catalog_entry

@router.delete("/product/{product_id}", response_model=None)
def delete_product(product_id: int, db: Session = Depends(deps.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return JSONResponse(status_code=200, content={"message": "No products found "})
    crud.delete_product_and_catalogs(db, product_id=product_id)

    return {"detail": "Product and related catalog entries deleted successfully"}



# @router.get("/catalogue/{user_id}", response_model=List[schemas.ProductCatalogResponse])
# def get_user_catalogue(user_id: int, db: Session = Depends(deps.get_db)):
#     products = crud.get_products_by_user_id(db, user_id=user_id)
#     if not products:
#         raise HTTPException(status_code=404, detail="No products found for the user")
    
#     catalogue_data = []
#     for product in products:
#         catalog_items = crud.get_catalog_by_product_id(db, product_id=product.id)
#         product_details = schemas.ProductDetail(**product.__dict__)
#         catalog_details_list = [schemas.CatalogDetail(**catalog_item.__dict__) for catalog_item in catalog_items]
        
#         for catalog_details in catalog_details_list:
#             catalogue_data.append(schemas.ProductCatalogResponse(product=product_details, catalog=catalog_details))

#     return catalogue_data