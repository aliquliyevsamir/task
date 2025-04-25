from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import string, random, httpx

app = FastAPI()
url_db: dict[str, str] = {}

class URLRequest(BaseModel):
    url: str

def generate_id(length=5) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

@app.post('/', status_code=201)
async def shorten_url(request: URLRequest):
    short_id = generate_id()
    url_db[short_id] = request.url
    return {"short_url": f"http://127.0.0.1:8080/{short_id}"}

# <-- сюда переносим get_random_number
@app.get("/random")
async def get_random_number():
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.randomnumberapi.com/api/v1.0/random?min=1&max=100"
        )
    if resp.status_code == 200:
        return {"random_number": resp.json()[0]}
    raise HTTPException(status_code=500, detail="Не удалось получить число")

# <-- а потом «ловушка»
@app.get("/{short_id}")
async def redirect_to_original(short_id: str):
    if short_id not in url_db:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=url_db[short_id], status_code=307)
