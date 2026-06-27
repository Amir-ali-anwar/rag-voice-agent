from motor.motor import AsyncIOMotorClient, AsyncIOMotorDatabase

client= AsyncIOMotorClient= None
dataabse = AsyncIOMotorDatabase = None

async def connect_to_mongo():
    """Create database connection"""
    global client, database

    try:
        client= AsyncIOMotorClient(settings.MONGO_URL, serverSelectionTimeoutMS=5000,
        connectTimeoutMS=30000,
            socketTimeoutMS=30000,)
        await client.admin.command("ping")
        database= client[settings.DB_NAME]
        logger.info(f"✅ Connected to MongoDB: {settings.DB_NAME}")
    except Exception as e:
        logger.error(f"❌ MongoDB Connection Failed: {str(e)}")



async def close_mongo_connection():
    """Close database connection"""
    if client:
        client.close()
        logger.info("✅ MongoDB Connection Closed") 


def get_database():
    """Get database connection"""
    return database

