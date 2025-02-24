import requests
import openai


def fetch_product_data(product_id):
    """Fetch product data from the API using the product ID."""
    url = f"https://backend.checkerchain.com/api/v1/products/{product_id}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get("data", [{}])[0]  # Get the first product item
    else:
        print("Error fetching product data:", response.status_code, response.text)
        return None


def get_trust_score(product_id):
    """Get the trust score for a product based on its ID."""
    # Fetch product data
    product_data = fetch_product_data(product_id)

    if not product_data:
        return None, None  # Return None if product data is not available

    # Extract relevant information from the product data
    product_description = product_data.get("description", "")
    owner_username = product_data.get("createdBy", {}).get("username", "")
    product_hype = "high"  # This can be adjusted based on your criteria

    # Construct the prompt for ChatGPT
    prompt = (
        f"I have a product called '{product_data.get('name')}', which is a {product_description}. "
        f"The owner of this product is a user with the username '{owner_username}'. "
        f"The product is currently generating a {product_hype} level of hype in the community. "
        "Could you provide a trustworthiness score for this product based on the following parameters?\n"
        "1. Owner Trustworthiness: Evaluate the credibility and reputation of the owner.\n"
        "2. Product Hype: Assess the current excitement and interest surrounding the product.\n"
        "3. Community Feedback: Consider any available reviews or feedback from users.\n"
        "4. Market Trends: Analyze the relevance of the product in the current market landscape.\n"
        "Please provide a trustworthiness score out of 100, along with a brief explanation of the reasoning behind the score."
    )

    # Call the OpenAI API (make sure to set your API key)
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo" depending on your access
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract the response content
    response_content = response["choices"][0]["message"]["content"]

    # Parse the response to extract trustworthiness score
    trustworthiness = None

    # Example parsing logic (you may need to adjust based on actual response format)
    for line in response_content.splitlines():
        if "Trustworthiness Score" in line:
            trustworthiness = int(line.split(":")[-1].strip())

    return trustworthiness


# Example usage
# product_id = "6303396acad553032d8fbb60"  # Replace with the actual product ID
# trustworthiness_score = get_trust_score(product_id)

# if trustworthiness_score is not None:
#     print("Trustworthiness Score (out of 100):", trustworthiness_score)
# else:
#     print("Failed to retrieve trustworthiness score.")
