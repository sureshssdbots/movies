from info import DATABASE_URI
import motor.motor_asyncio
import uuid  # for generating unique IDs
import datetime  # for timestamping
import pymongo  # for indexing

class JsTopDB:
    def __init__(self, db_uri):
        # Connect to MongoDB
        self.client = motor.motor_asyncio.AsyncIOMotorClient(db_uri)
        self.db = self.client["movie_series_db"]
        self.collection = self.db["movie_series"]
        
        # Create indexes to speed up searches
        self.collection.create_index([("group_id", pymongo.ASCENDING), ("name", pymongo.ASCENDING), ("search_count", pymongo.DESCENDING)])

    async def set_movie_series_names(self, names, group_id, user_id=None):
        # Input Validation
        if not names.strip() or not group_id.strip():
            raise ValueError("Movie/Series name and Group ID cannot be empty!")
        
        movie_series_list = names.split(",")
        for name in movie_series_list:
            search_id = str(uuid.uuid4())  # Generate unique search_id
            timestamp = datetime.datetime.now()

            try:
                await self.collection.update_one(
                    {"name": name.strip(), "group_id": group_id},
                    {
                        "$inc": {"search_count": 1},
                        "$push": {"search_history": {"user_id": user_id, "timestamp": timestamp}} if user_id else {},
                        "$set": {"timestamp": timestamp}
                    },
                    upsert=True
                )
            except Exception as e:
                print(f"Error while adding movie/series: {e}")
                raise

    async def get_movie_series_names(self, group_id, page=1, per_page=10):
        # Input Validation
        if not group_id.strip():
            raise ValueError("Group ID cannot be empty!")
        
        try:
            # Fetch the movie/series names sorted by search count and timestamp
            cursor = self.collection.find({"group_id": group_id}).skip((page-1) * per_page).limit(per_page).sort([("search_count", pymongo.DESCENDING), ("timestamp", pymongo.DESCENDING)])
            names = [document["name"] async for document in cursor]
            return names
        except Exception as e:
            print(f"Error while fetching movie/series names: {e}")
            raise

    async def clear_movie_series_names(self, group_id):
        # Input Validation
        if not group_id.strip():
            raise ValueError("Group ID cannot be empty!")
        
        try:
            await self.collection.delete_many({"group_id": group_id})
        except Exception as e:
            print(f"Error while clearing movie/series names: {e}")
            raise

    async def get_search_history(self, group_id):
        try:
            cursor = self.collection.find({"group_id": group_id})
            for doc in cursor:
                print(f"Movie/Series: {doc['name']}, Search History: {doc['search_history']}")
        except Exception as e:
            print(f"Error while fetching search history: {e}")
            raise

async def main():
    movie_series_db = JsTopDB(DATABASE_URI)
    while True:
        try:
            # Get user input
            search_input = input("Enter the movie/series name: ")
            group_id = input("Enter group ID: ")
            user_id = input("Enter user ID (optional): ")
            
            # Validate and add the movie/series name
            await movie_series_db.set_movie_series_names(search_input, group_id, user_id)
            print("Movie/Series name added successfully.")
            
            # Fetch and display the updated list of movie/series names
            names = await movie_series_db.get_movie_series_names(group_id)
            print("Updated Movie/Series Names (Sorted by Search Count and Timestamp):")
            for name in names:
                print(name)
            
            # Option to view search history
            show_history = input("Do you want to view search history for this group? (yes/no): ")
            if show_history.lower() == "yes":
                await movie_series_db.get_search_history(group_id)

            # Option to clear movie/series names
            clear_input = input("Do you want to clear names for this group? (yes/no): ")
            if clear_input.lower() == "yes":
                await movie_series_db.clear_movie_series_names(group_id)
                print("Names cleared successfully.")

        except ValueError as ve:
            print(f"Input Error: {ve}")
        except Exception as e:
            print(f"Unexpected Error: {e}")
