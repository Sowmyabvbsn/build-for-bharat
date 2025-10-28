from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# UP Districts Master Data (75 districts)
UP_DISTRICTS = [
    {"code": "UP001", "name": "Agra", "name_hi": "आगरा", "region": "West"},
    {"code": "UP002", "name": "Aligarh", "name_hi": "अलीगढ़", "region": "West"},
    {"code": "UP003", "name": "Allahabad", "name_hi": "प्रयागराज", "region": "South"},
    {"code": "UP004", "name": "Ambedkar Nagar", "name_hi": "अम्बेडकर नगर", "region": "East"},
    {"code": "UP005", "name": "Amethi", "name_hi": "अमेठी", "region": "Central"},
    {"code": "UP006", "name": "Amroha", "name_hi": "अमरोहा", "region": "West"},
    {"code": "UP007", "name": "Auraiya", "name_hi": "औरैया", "region": "West"},
    {"code": "UP008", "name": "Azamgarh", "name_hi": "आजमगढ़", "region": "East"},
    {"code": "UP009", "name": "Baghpat", "name_hi": "बागपत", "region": "West"},
    {"code": "UP010", "name": "Bahraich", "name_hi": "बहराइच", "region": "North"},
    {"code": "UP011", "name": "Ballia", "name_hi": "बलिया", "region": "East"},
    {"code": "UP012", "name": "Balrampur", "name_hi": "बलरामपुर", "region": "North"},
    {"code": "UP013", "name": "Banda", "name_hi": "बांदा", "region": "South"},
    {"code": "UP014", "name": "Barabanki", "name_hi": "बाराबंकी", "region": "Central"},
    {"code": "UP015", "name": "Bareilly", "name_hi": "बरेली", "region": "North"},
    {"code": "UP016", "name": "Basti", "name_hi": "बस्ती", "region": "East"},
    {"code": "UP017", "name": "Bhadohi", "name_hi": "भदोही", "region": "South"},
    {"code": "UP018", "name": "Bijnor", "name_hi": "बिजनौर", "region": "West"},
    {"code": "UP019", "name": "Budaun", "name_hi": "बदायूं", "region": "North"},
    {"code": "UP020", "name": "Bulandshahr", "name_hi": "बुलंदशहर", "region": "West"},
    {"code": "UP021", "name": "Chandauli", "name_hi": "चंदौली", "region": "East"},
    {"code": "UP022", "name": "Chitrakoot", "name_hi": "चित्रकूट", "region": "South"},
    {"code": "UP023", "name": "Deoria", "name_hi": "देवरिया", "region": "East"},
    {"code": "UP024", "name": "Etah", "name_hi": "एटा", "region": "West"},
    {"code": "UP025", "name": "Etawah", "name_hi": "इटावा", "region": "West"},
    {"code": "UP026", "name": "Ayodhya", "name_hi": "अयोध्या", "region": "Central"},
    {"code": "UP027", "name": "Farrukhabad", "name_hi": "फर्रुखाबाद", "region": "West"},
    {"code": "UP028", "name": "Fatehpur", "name_hi": "फतेहपुर", "region": "Central"},
    {"code": "UP029", "name": "Firozabad", "name_hi": "फिरोजाबाद", "region": "West"},
    {"code": "UP030", "name": "Gautam Buddha Nagar", "name_hi": "गौतम बुद्ध नगर", "region": "West"},
    {"code": "UP031", "name": "Ghaziabad", "name_hi": "गाजियाबाद", "region": "West"},
    {"code": "UP032", "name": "Ghazipur", "name_hi": "गाजीपुर", "region": "East"},
    {"code": "UP033", "name": "Gonda", "name_hi": "गोंडा", "region": "North"},
    {"code": "UP034", "name": "Gorakhpur", "name_hi": "गोरखपुर", "region": "East"},
    {"code": "UP035", "name": "Hamirpur", "name_hi": "हमीरपुर", "region": "South"},
    {"code": "UP036", "name": "Hapur", "name_hi": "हापुड़", "region": "West"},
    {"code": "UP037", "name": "Hardoi", "name_hi": "हरदोई", "region": "Central"},
    {"code": "UP038", "name": "Hathras", "name_hi": "हाथरस", "region": "West"},
    {"code": "UP039", "name": "Jalaun", "name_hi": "जालौन", "region": "South"},
    {"code": "UP040", "name": "Jaunpur", "name_hi": "जौनपुर", "region": "East"},
    {"code": "UP041", "name": "Jhansi", "name_hi": "झांसी", "region": "South"},
    {"code": "UP042", "name": "Kannauj", "name_hi": "कन्नौज", "region": "Central"},
    {"code": "UP043", "name": "Kanpur Dehat", "name_hi": "कानपुर देहात", "region": "Central"},
    {"code": "UP044", "name": "Kanpur Nagar", "name_hi": "कानपुर नगर", "region": "Central"},
    {"code": "UP045", "name": "Kasganj", "name_hi": "कासगंज", "region": "West"},
    {"code": "UP046", "name": "Kaushambi", "name_hi": "कौशाम्बी", "region": "South"},
    {"code": "UP047", "name": "Kushinagar", "name_hi": "कुशीनगर", "region": "East"},
    {"code": "UP048", "name": "Lakhimpur Kheri", "name_hi": "लखीमपुर खीरी", "region": "North"},
    {"code": "UP049", "name": "Lalitpur", "name_hi": "ललितपुर", "region": "South"},
    {"code": "UP050", "name": "Lucknow", "name_hi": "लखनऊ", "region": "Central"},
    {"code": "UP051", "name": "Maharajganj", "name_hi": "महाराजगंज", "region": "East"},
    {"code": "UP052", "name": "Mahoba", "name_hi": "महोबा", "region": "South"},
    {"code": "UP053", "name": "Mainpuri", "name_hi": "मैनपुरी", "region": "West"},
    {"code": "UP054", "name": "Mathura", "name_hi": "मथुरा", "region": "West"},
    {"code": "UP055", "name": "Mau", "name_hi": "मऊ", "region": "East"},
    {"code": "UP056", "name": "Meerut", "name_hi": "मेरठ", "region": "West"},
    {"code": "UP057", "name": "Mirzapur", "name_hi": "मिर्जापुर", "region": "South"},
    {"code": "UP058", "name": "Moradabad", "name_hi": "मुरादाबाद", "region": "North"},
    {"code": "UP059", "name": "Muzaffarnagar", "name_hi": "मुजफ्फरनगर", "region": "West"},
    {"code": "UP060", "name": "Pilibhit", "name_hi": "पीलीभीत", "region": "North"},
    {"code": "UP061", "name": "Pratapgarh", "name_hi": "प्रतापगढ़", "region": "South"},
    {"code": "UP062", "name": "Raebareli", "name_hi": "रायबरेली", "region": "Central"},
    {"code": "UP063", "name": "Rampur", "name_hi": "रामपुर", "region": "North"},
    {"code": "UP064", "name": "Saharanpur", "name_hi": "सहारनपुर", "region": "West"},
    {"code": "UP065", "name": "Sambhal", "name_hi": "संभल", "region": "West"},
    {"code": "UP066", "name": "Sant Kabir Nagar", "name_hi": "संत कबीर नगर", "region": "East"},
    {"code": "UP067", "name": "Shahjahanpur", "name_hi": "शाहजहांपुर", "region": "North"},
    {"code": "UP068", "name": "Shamli", "name_hi": "शामली", "region": "West"},
    {"code": "UP069", "name": "Shravasti", "name_hi": "श्रावस्ती", "region": "North"},
    {"code": "UP070", "name": "Siddharthnagar", "name_hi": "सिद्धार्थनगर", "region": "East"},
    {"code": "UP071", "name": "Sitapur", "name_hi": "सीतापुर", "region": "Central"},
    {"code": "UP072", "name": "Sonbhadra", "name_hi": "सोनभद्र", "region": "South"},
    {"code": "UP073", "name": "Sultanpur", "name_hi": "सुल्तानपुर", "region": "East"},
    {"code": "UP074", "name": "Unnao", "name_hi": "उन्नाव", "region": "Central"},
    {"code": "UP075", "name": "Varanasi", "name_hi": "वाराणसी", "region": "South"}
]

# Models
class District(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code: str
    name: str
    name_hi: str
    region: str

class MGNREGAData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    district_code: str
    district_name: str
    month: str
    year: int
    # Key metrics
    job_cards_issued: int
    active_workers: int
    person_days_generated: int
    average_days_per_household: float
    works_completed: int
    works_ongoing: int
    expenditure_crores: float
    women_participation_percent: float
    sc_st_participation_percent: float
    # Performance indicators
    performance_score: float  # 0-100
    performance_grade: str  # A, B, C, D
    last_updated: str

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

class TrendData(BaseModel):
    month: str
    year: int
    person_days: int
    expenditure: float
    active_workers: int

# Helper functions
async def init_districts():
    """Initialize districts collection if empty"""
    count = await db.districts.count_documents({})
    if count == 0:
        logger.info("Initializing districts collection...")
        await db.districts.insert_many(UP_DISTRICTS)
        logger.info(f"Inserted {len(UP_DISTRICTS)} districts")

def generate_mock_data(district_code: str, district_name: str, month: int, year: int) -> dict:
    """Generate realistic mock MGNREGA data"""
    import random
    
    # Base values with some randomization
    job_cards = random.randint(50000, 200000)
    active_workers = int(job_cards * random.uniform(0.4, 0.7))
    person_days = active_workers * random.randint(30, 90)
    avg_days = person_days / max(active_workers, 1)
    
    works_completed = random.randint(100, 500)
    works_ongoing = random.randint(50, 300)
    expenditure = person_days * random.uniform(200, 300) / 10000000  # In crores
    
    women_participation = random.uniform(48, 62)
    sc_st_participation = random.uniform(25, 45)
    
    # Calculate performance score based on multiple factors
    score = 0
    if avg_days >= 50:
        score += 30
    elif avg_days >= 30:
        score += 20
    else:
        score += 10
    
    if women_participation >= 50:
        score += 20
    else:
        score += 10
    
    if person_days >= 3000000:
        score += 25
    elif person_days >= 2000000:
        score += 15
    else:
        score += 5
    
    completion_rate = works_completed / max(works_completed + works_ongoing, 1)
    score += completion_rate * 25
    
    # Grade based on score
    if score >= 80:
        grade = "A"
    elif score >= 60:
        grade = "B"
    elif score >= 40:
        grade = "C"
    else:
        grade = "D"
    
    return {
        "district_code": district_code,
        "district_name": district_name,
        "month": f"{year}-{month:02d}",
        "year": year,
        "job_cards_issued": job_cards,
        "active_workers": active_workers,
        "person_days_generated": person_days,
        "average_days_per_household": round(avg_days, 2),
        "works_completed": works_completed,
        "works_ongoing": works_ongoing,
        "expenditure_crores": round(expenditure, 2),
        "women_participation_percent": round(women_participation, 2),
        "sc_st_participation_percent": round(sc_st_participation, 2),
        "performance_score": round(score, 2),
        "performance_grade": grade,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

async def fetch_or_generate_data(district_code: str, district_name: str, month: int, year: int) -> dict:
    """Fetch from cache or generate new data"""
    # Check cache first
    month_str = f"{year}-{month:02d}"
    cached = await db.mgnrega_data.find_one({
        "district_code": district_code,
        "month": month_str
    }, {"_id": 0})
    
    if cached:
        return cached
    
    # Generate mock data (in production, this would call data.gov.in API)
    data = generate_mock_data(district_code, district_name, month, year)
    
    # Cache it
    await db.mgnrega_data.insert_one(data)
    
    return data

# Routes
@api_router.get("/")
async def root():
    return {"message": "MGNREGA Data API - Uttar Pradesh"}

@api_router.get("/districts", response_model=List[District])
async def get_districts():
    """Get all UP districts"""
    districts = await db.districts.find({}, {"_id": 0}).to_list(100)
    return districts

@api_router.get("/districts/{district_code}/current")
async def get_district_current_data(district_code: str):
    """Get current month data for a district"""
    # Get district info
    district = await db.districts.find_one({"code": district_code}, {"_id": 0})
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    # Get current month data
    now = datetime.now()
    data = await fetch_or_generate_data(district_code, district['name'], now.month, now.year)
    
    return data

@api_router.get("/districts/{district_code}/trends")
async def get_district_trends(district_code: str, months: int = 12):
    """Get historical trends for a district"""
    district = await db.districts.find_one({"code": district_code}, {"_id": 0})
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    # Generate data for past months
    now = datetime.now()
    trends = []
    
    for i in range(months):
        month = now.month - i
        year = now.year
        
        while month <= 0:
            month += 12
            year -= 1
        
        data = await fetch_or_generate_data(district_code, district['name'], month, year)
        trends.append({
            "month": data['month'],
            "year": data['year'],
            "person_days": data['person_days_generated'],
            "expenditure": data['expenditure_crores'],
            "active_workers": data['active_workers'],
            "performance_score": data['performance_score']
        })
    
    return {"district": district, "trends": list(reversed(trends))}

@api_router.get("/districts/compare")
async def compare_districts(codes: str):
    """Compare multiple districts"""
    district_codes = codes.split(",")
    
    if len(district_codes) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 districts for comparison")
    
    now = datetime.now()
    comparisons = []
    
    for code in district_codes:
        district = await db.districts.find_one({"code": code.strip()}, {"_id": 0})
        if district:
            data = await fetch_or_generate_data(code.strip(), district['name'], now.month, now.year)
            comparisons.append(data)
    
    return {"comparisons": comparisons}

@api_router.post("/location/detect")
async def detect_district(location: LocationRequest):
    """Detect district from coordinates using reverse geocoding"""
    try:
        async with httpx.AsyncClient() as client:
            # Using Nominatim (OpenStreetMap) - free geocoding
            response = await client.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": location.latitude,
                    "lon": location.longitude,
                    "format": "json",
                    "addressdetails": 1
                },
                headers={"User-Agent": "MGNREGA-App/1.0"}
            )
            
            if response.status_code == 200:
                data = response.json()
                address = data.get("address", {})
                
                # Try to match district
                district_name = address.get("state_district") or address.get("county") or address.get("suburb")
                
                if district_name:
                    # Find matching district in our database
                    district = await db.districts.find_one(
                        {"name": {"$regex": district_name, "$options": "i"}},
                        {"_id": 0}
                    )
                    
                    if district:
                        return {"success": True, "district": district}
                
                return {"success": False, "message": "Could not determine district from location"}
            
            return {"success": False, "message": "Geocoding service unavailable"}
            
    except Exception as e:
        logger.error(f"Location detection error: {e}")
        return {"success": False, "message": "Location detection failed"}

@api_router.get("/state/overview")
async def get_state_overview():
    """Get state-level overview statistics"""
    now = datetime.now()
    month_str = f"{now.year}-{now.month:02d}"
    
    # Get all districts current data
    all_data = await db.mgnrega_data.find({"month": month_str}, {"_id": 0}).to_list(100)
    
    # Calculate state-level aggregates
    total_active_workers = sum(d['active_workers'] for d in all_data)
    total_person_days = sum(d['person_days_generated'] for d in all_data)
    total_expenditure = sum(d['expenditure_crores'] for d in all_data)
    
    avg_performance = sum(d['performance_score'] for d in all_data) / len(all_data) if all_data else 0
    
    # Count districts by grade
    grade_distribution = {"A": 0, "B": 0, "C": 0, "D": 0}
    for d in all_data:
        grade_distribution[d['performance_grade']] += 1
    
    return {
        "total_districts": len(UP_DISTRICTS),
        "total_active_workers": total_active_workers,
        "total_person_days": total_person_days,
        "total_expenditure_crores": round(total_expenditure, 2),
        "average_performance_score": round(avg_performance, 2),
        "grade_distribution": grade_distribution,
        "top_performers": sorted(all_data, key=lambda x: x['performance_score'], reverse=True)[:5],
        "month": month_str
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    await init_districts()
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
