from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .logging_config import logger
from time import time

from .database import init_db, engine
from sqlmodel import Session
from .routers import store, users, auth, purchase

init_db()

app = FastAPI(
    title="XtraMiles - More on the go...",
    summary = "Reward customers with points for every gallon of fuel purchased while simplifying store management.",
    description = """
    FuelRewards API is a robust solution for managing stores, customers, and reward points for fuel purchases. 🚗⛽

        ## Core Features

        ### **Users**
        - **Register and Manage Accounts**: Users can register with their details and manage their profiles.
        - **Reward Points**: Earn points for every gallon of fuel purchased.
        - **Track Showers**: Monitor shower rewards for loyalty programs.
        - **Secure Authentication**: Passwords are securely hashed, ensuring user safety.

        ### **Stores**
        - **Store Management**: Create, view, and update store details, including fuel prices.
        - **Fuel Price Updates**: Stores can manage and adjust fuel prices to reflect current rates.

        ### **Purchases**
        - **Record Transactions**: Track fuel and grocery purchases, awarding points to customers.
        - **Points System**: Automatically calculate and award points based on purchases.
        - **Shower Rewards**: Manage whether customers are awarded showers as part of their transactions.
        - **Detailed Timestamps**: All purchases are tracked with `created_at` and `updated_at` timestamps for better auditing.

        ## Tokens and Security
        - **Authentication Tokens**: Uses JWT tokens for secure access.
        - **User Identity Management**: Token-based identification ensures safe and private transactions.

        ## Admin Features (Future Scope)
        - Comprehensive reporting and analytics for store and user activity.
        - Configurable reward rules for different promotions and campaigns.

    FuelRewards simplifies and enhances the fueling experience, creating value for both stores and customers. Ready to reward your journey? 🚀
    """,
    Version="1.0",
    )
# Set up allowed origins for CORS
origins = [
    "http://localhost:3000",  # Add your frontend domain here
    "https://example.com",    # Add production domain here
]

# Add CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Logging Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time()
    ip_address = request.client.host
    endpoint = request.url.path
    method = request.method
    logger.info(f"Incoming request: IP={ip_address}, Endpoint={endpoint}, Method={method}")

    # Process the request
    response = await call_next(request)

    # Log additional response info
    process_time = time() - start_time
    status_code = response.status_code
    logger.info(f"Completed request: Endpoint={endpoint}, Status={status_code}, Time={process_time:.2f}s")
    return response

# Add Custom Middleware (Example)
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # Modify request headers or perform other actions here
    logger.info("Custom Middleware: Pre-processing request")
    response = await call_next(request)
    # Add custom response headers or perform post-processing
    response.headers["X-Custom-Header"] = "XtraMiles"
    logger.info("Custom Middleware: Post-processing request")
    return response

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# Routers
app.include_router(auth.router)
app.include_router(store.router)
app.include_router(users.router)
app.include_router(purchase.router)



@app.get("/", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def home(request:Request):
    return{"message": "Hello World!!!"}

 