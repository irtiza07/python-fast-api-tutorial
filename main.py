import time

from enum import Enum
from typing import List
from typing import Optional

import uvicorn
from fastapi import Cookie, FastAPI, Header, status, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


def write_notification(email, message):
    print("Sending email notification in background..")
    time.sleep(5)
    print(f"Email sent to {email} with message: {message} ")


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]


class Cart(BaseModel):
    items: List[str]
    totalPrice: int
    promotionsAttached: bool


class Course(str, Enum):
    CHEMISTRY = "chemistry"
    PHYSICS = "physics"
    MATH = "math"


class CourseEntity(BaseModel):
    id: int
    name: str
    description: str = Field(
        min_length=5, description="Proper description of the course materials!"
    )
    language: Optional[str]
    rating: int
    tags: List[str] = Field(default=["public"])


app = FastAPI(debug=True)

#! Configure CORS to allow cross origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#! Automatic conversion
#! Data validation when typed
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


#! Enumerated path parameters
#! Query parameters [Optional & Required]
#! Implicit enforcement
#! Talk about Pydantic Field for extra validation
@app.get("/courses/{course}")
async def get_course(course: Course, language: str, minRating: int = 0):
    if course == Course.CHEMISTRY:
        return {
            "description": "Let's learn about chemicals!",
            "language": language,
            "minRating": minRating,
        }

    if course == Course.PHYSICS:
        return {
            "description": "Let's learn about physical matters!",
            "language": language,
            "minRating": minRating,
        }

    if course == Course.MATH:
        return {
            "description": "Let's learn about numbers!",
            "language": language,
            "minRating": minRating,
        }


#! Automatically convert JSON --> Python and vice versa
#! Validate request body and send errors back
#! Add models in Swagger
@app.post("/courses/")
async def create_course(course: CourseEntity):
    print("Course created successfully")
    return course


#! Reading browser cookies!
#! Reading request headers
@app.get("/students/")
async def get_students(
    token: Optional[str] = Cookie(None),
    ads_id: Optional[str] = Cookie(None),
    user_agent: Optional[str] = Header(None),
):
    return {
        "cookie_token_found": token,
        "ads_id_in_browser": ads_id,
        "incoming_user_agent": user_agent,
    }


#! Typed response [+ Documentation]
#! Automatic conversions and validations
#! Talk about explicit status codes
@app.get("/current_cart", response_model=Cart, status_code=status.HTTP_200_OK)
async def get_cart():
    return Cart(
        items=["shampoo", "chocolates", "soap"],
        totalPrice=1500,
        promotionsAttached=False,
    )


#! Throw explicit HTTP errors
@app.get("/flights/{flight_id}")
async def get_flights(flight_id: int):
    if flight_id not in [1, 2, 3]:
        raise HTTPException(status_code=404, detail="Flight not found")
    else:
        return {"message": "Fly high!"}


#! Kick off background tasks
@app.get("/send_email/{email}")
async def send_email(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="Hellooo world!!")


#! Or just run uvicorn main:app --host 0.0.0.0 --port 80 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
