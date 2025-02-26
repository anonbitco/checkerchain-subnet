from dataclasses import dataclass
from typing import List
import requests
from template.utils.sqlite_utils import add_product, get_products, update_product_status
from template.types.checker_chain import Product, ProductApiResponse, ProductsApiResponse


@dataclass
class FetchProductsReturnType:
    unmined_products: List[str]
    reward_items: List[Product]


def fetch_products():
    url = "https://api.checkerchain.com/api/v1/products?page=1&limit=100"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return FetchProductsReturnType([], [])

    data = ProductsApiResponse.from_dict(response.json())

    if not (isinstance(data, ProductsApiResponse)):
        return FetchProductsReturnType([], [])

    products = data.data.products

    # Fetch existing product IDs from the database
    all_products = get_products()
    existing_product_ids = {p["_id"] for p in all_products}
    unmined_products: list[str] = []
    reward_items: list[Product] = []

    for product in products:
        if product.status == "published" and product._id not in existing_product_ids:
            add_product(product._id, product.name)
            unmined_products.append(product._id)
        if product.status == "reviewed" and product._id in existing_product_ids:
            reward_items.append(product)

    return FetchProductsReturnType(unmined_products, reward_items)


def fetch_product_data(product_id):
    """Fetch product data from the API using the product ID."""
    url = f"https://backend.checkerchain.com/api/v1/products/{product_id}"
    response = requests.get(url)

    if response.status_code == 200:
        productData = ProductApiResponse.from_dict(response.json()).data
        if not (isinstance(productData, ProductApiResponse)):
            return None
        return productData.data
    else:
        print("Error fetching product data:",
              response.status_code, response.text)
        return None


def get_and_update_checker_chain_product_list():
    url = "https://backend.checkerchain.com/api/v1/products?page=1&limit=30"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Error: {response.status_code}"

    data = response.json()

    if "data" not in data or "products" not in data["data"]:
        return "Invalid data structure."

    products = data["data"]["products"]
    if not products:
        return "No products found."

    # Fetch existing product IDs from the database
    all_products = get_products()
    existing_product_ids = {p["_id"] for p in all_products}
    unmined_products = [
        product for product in all_products if not product["mining_done"]
    ]

    for product in products:
        if product["_id"] not in existing_product_ids:
            if not product.isReviewed:
                add_product(product["_id"], product["name"])
                unmined_products.append(product["_id"])

        # Update all products status:
        if product.isReviewed:
            update_product_status(
                product["_id"],
                check_chain_review_done=True,
                trust_score=product["trustScore"],
            )

    return unmined_products


# TODO:: replace it with real api call
def dummy_get_current_epoch_reviewed_products():
    return [
        {"_id": 1, "name": "Product 1", "trustScore": 90},
        {"_id": 2, "name": "Product 2", "trustScore": 80},
        {"_id": 3, "name": "Product 3", "trustScore": 70},
    ]


# 1 days epoch (23 hr 59 min, once score is out review wont be counted)
# to review products available in checker chain
#
