import sqlite3


def get_db_connection():
    """Helper function to get a database connection."""
    conn = sqlite3.connect("checker_db.db")
    conn.row_factory = (
        sqlite3.Row
    )  # Enable dictionary cursor for better readability (optional)
    return conn


def execute_query(query, params=(), commit=False, fetch=False):
    """Helper function to execute a query (insert, update, delete) and optionally commit or fetch results."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)

    if commit:
        conn.commit()

    # Fetch results if needed
    results = None
    if fetch:
        results = cursor.fetchall()

    conn.close()
    return results


def create_db():
    """Creates the tables in the database."""
    # Create 'products' table with the new boolean fields
    execute_query(
        """
        CREATE TABLE IF NOT EXISTS products (
            _id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            trust_score FLOAT NOT NULL DEFAULT 0,
            check_chain_review_done BOOLEAN NOT NULL DEFAULT 0,
            mining_done BOOLEAN NOT NULL DEFAULT 0,
            rewards_distributed BOOLEAN NOT NULL DEFAULT 0
        )
    """
    )

    # Create 'miner_predictions' table
    execute_query(
        """
        CREATE TABLE IF NOT EXISTS miner_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            miner_id TEXT NOT NULL,
            prediction INTEGER,
            FOREIGN KEY (product_id) REFERENCES products (_id)
        )
    """
    )


def add_product(
    _id,
    name,
    trust_score=0,
    check_chain_review_done=False,
    mining_done=False,
    rewards_distributed=False,
):
    """Adds a product to the database."""
    execute_query(
        """
        INSERT INTO products (_id, name, trust_score, check_chain_review_done, mining_done, rewards_distributed)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            _id,
            name,
            trust_score,
            check_chain_review_done,
            mining_done,
            rewards_distributed,
        ),
        commit=True,
    )


def remove_product(_id):
    """Removes a product from the database."""
    execute_query(
        """
        DELETE FROM products WHERE _id = ?
    """,
        (_id,),
        commit=True,
    )


def add_prediction(product_id, miner_id, prediction):
    """Adds a prediction to the database."""
    execute_query(
        """
        INSERT INTO miner_predictions (product_id, miner_id, prediction)
        VALUES (?, ?, ?)
    """,
        (product_id, miner_id, prediction),
        commit=True,
    )


def remove_prediction(id):
    """Removes a prediction from the database."""
    execute_query(
        """
        DELETE FROM miner_predictions WHERE id = ?
    """,
        (id,),
        commit=True,
    )


def update_product_status(
    _id,
    check_chain_review_done=None,
    mining_done=None,
    rewards_distributed=None,
    trust_score=0,
):
    """Updates the status fields of a product."""
    # Start building the query
    query = "UPDATE products SET "
    params = []

    if check_chain_review_done is not None:
        query += "check_chain_review_done = ?, "
        params.append(check_chain_review_done)

    if mining_done is not None:
        query += "mining_done = ?, "
        params.append(mining_done)

    if rewards_distributed is not None:
        query += "rewards_distributed = ?, "
        params.append(rewards_distributed)

    if trust_score is not None:
        query += "trust_score = ?, "
        params.append(trust_score)

    # Remove the trailing comma and space
    query = query.rstrip(", ")

    query += " WHERE _id = ?"
    params.append(_id)

    # Execute the query
    execute_query(query, tuple(params), commit=True)


def get_products():
    """Fetches all products from the database."""
    return execute_query(
        """
        SELECT * FROM products
    """,
        fetch=True,
    )


def delete_a_product(product_id: str):
    """Delete all predictions from the database for product_id."""
    execute_query(
        """
            DELETE FROM miner_predictions WHERE product_id = %s
        """,
        params=(product_id)
    )
    """Deletes a product from the database by product_id."""
    return execute_query(
        """
            DELETE FROM products WHERE _id = %s
        """,
        params=(product_id)
    )


def get_a_product(
    check_chain_review_done=None, mining_done=None, rewards_distributed=None
):
    """Fetches one product from the database with optional filtering."""
    try:
        # Build the base query
        query = "SELECT * FROM products WHERE 1=1"

        # Add conditions based on the parameters provided
        params = []

        if mining_done is not None:
            query += " AND mining_done = ?"
            params.append(mining_done)

        if check_chain_review_done is not None:
            query += " AND check_chain_review_done = ?"
            params.append(check_chain_review_done)

        if rewards_distributed is not None:
            query += " AND rewards_distributed = ?"
            params.append(rewards_distributed)

        # Limit the query to return only one product
        query += " LIMIT 1"

        # Execute the query with the dynamic parameters
        result = execute_query(query, fetch=True, params=params)

        # Return the result, or None if no product is found
        return result[0] if result else None

    except Exception as e:
        return f"Error occurred: {e}"


def get_predictions_for_product(product_id):
    """Fetches all predictions for a specific product."""
    return execute_query(
        """
        SELECT * FROM miner_predictions WHERE product_id = ?
    """,
        (product_id,),
        fetch=True,
    )


# Example of usage:
if __name__ == "__main__":
    # Creating tables
    create_db()

    # Adding products with the new status fields
    add_product(
        "P001",
        "Product 1",
        check_chain_review_done=True,
        mining_done=False,
        rewards_distributed=True,
    )
    add_product(
        "P002",
        "Product 2",
        check_chain_review_done=False,
        mining_done=True,
        rewards_distributed=False,
    )

    # Adding predictions
    add_prediction("P001", "Miner01", 100)
    add_prediction("P001", "Miner02", 150)
    add_prediction("P002", "Miner03", 200)

    # Fetching all products
    products = get_products()
    print("Products:")
    for product in products:
        print(dict(product))  # Convert to dictionary for easier reading

    # Fetching predictions for a specific product
    predictions = get_predictions_for_product("P001")
    print("\nPredictions for Product P001:")
    for prediction in predictions:
        print(dict(prediction))  # Convert to dictionary for easier reading

    # Updating product status
    update_product_status(
        "P001", check_chain_review_done=False, mining_done=True)

    # Removing a product
    remove_product("P002")

    # Removing a prediction
    remove_prediction(1)


def dummy_get_miner_prediction_for_products(product_ids):
    return [
        {"_id": 1, "miner_id": 1, "prediction": 90},
        {"_id": 2, "miner_id": 2, "prediction": 80},
        {"_id": 3, "miner_id": 3, "prediction": 70},
    ]
