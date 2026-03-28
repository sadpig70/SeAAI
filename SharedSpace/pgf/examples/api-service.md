# Practical Example: REST API Service

## Gantree Design

```
APIService // REST API service (in-progress) @v:1.0

    DataLayer // Data layer (done)
        DatabaseSchema // DB schema design (done)
            create_tables // Table creation (done)
            create_indexes // Index creation (done)
        ORMModels // ORM model definition (done)

    BusinessLogic // Business logic (in-progress) @dep:DataLayer
        UserService // User service (done)
            AI_validate_user_input // Input validation (done)
            create_user // User creation (done)
            authenticate_user // Authentication (done)
        ProductService // Product service (in-progress)
            AI_categorize_product // Product categorization (in-progress)
            search_products // Product search (designing)

    APILayer // API layer (designing) @dep:BusinessLogic
        [parallel]
        UserEndpoints // User endpoints (designing)
            POST_users // POST /users (designing)
            POST_auth // POST /auth (designing)
        ProductEndpoints // Product endpoints (designing)
            GET_products // GET /products (designing)
            POST_products // POST /products (designing)
        [/parallel]

    Testing // Testing (blocked) @dep:APILayer
        AI_generate_test_cases // Test case generation (blocked)
        run_integration_tests // Integration test execution (blocked)
```

## PPR Detail — ProductService Node

```python
def product_service(
    product_data: dict,
    action: Literal["categorize", "search"],
) -> dict:
    """Product service — AI categorization + deterministic search"""

    if action == "categorize":
        # AI cognition: infer category from product description
        category: str = AI_categorize_product(
            name=product_data["name"],
            description=product_data["description"],
        )
        # Deterministic: save to DB
        save_product(product_data, category=category)
        return {"category": category, "saved": True}

    elif action == "search":
        # Deterministic: execute query
        query = build_search_query(product_data.get("filters", {}))
        results = execute_query(query)
        # AI cognition: rank results
        ranked = AI_rank_relevance(results, product_data.get("query", ""))
        return {"results": ranked, "total": len(results)}
```

## Execution Flow Interpretation

```
1. DataLayer (done) → skip
2. BusinessLogic (in-progress)
   - UserService (done) → skip
   - ProductService (in-progress) → execute per PPR def block
     - AI_categorize_product: AI cognition (Recognition)
     - search_products: designing → stub only
3. APILayer (designing) → @dep:BusinessLogic incomplete, waiting
4. Testing (blocked) → fully skip
```
