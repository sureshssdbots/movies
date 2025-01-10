import pymongo
from info import DATABASE_URI, DATABASE_NAME
import logging

# Setup Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Changed to DEBUG for more detailed logging

# Create MongoDB client and access the database
try:
    myclient = pymongo.MongoClient(DATABASE_URI)
    mydb = myclient[DATABASE_NAME]
except pymongo.errors.ConnectionError as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise

class UserTracker:
    def __init__(self):
        # Initializing MongoDB collections
        self.user_collection = mydb["referusers"]
        self.refer_collection = mydb["refers"]

    def add_user(self, user_id):
        try:
            if not self.is_user_in_list(user_id):
                self.user_collection.insert_one({'user_id': user_id})
                logger.info(f"User {user_id} added successfully.")
            else:
                logger.warning(f"User {user_id} already exists.")
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            raise

    def remove_user(self, user_id):
        try:
            result = self.user_collection.delete_one({'user_id': user_id})
            if result.deleted_count > 0:
                logger.info(f"User {user_id} removed successfully.")
            else:
                logger.warning(f"User {user_id} not found.")
        except Exception as e:
            logger.error(f"Error removing user {user_id}: {e}")
            raise

    def is_user_in_list(self, user_id):
        try:
            user = self.user_collection.find_one({'user_id': user_id})
            return bool(user)
        except Exception as e:
            logger.error(f"Error checking if user {user_id} exists: {e}")
            raise

    def add_refer_points(self, user_id: int, points: int):
        try:
            # Update or insert the refer points for a user
            self.refer_collection.update_one(
                {'user_id': user_id},
                {'$set': {'points': points}},
                upsert=True
            )
            logger.info(f"Points for user {user_id} set to {points}.")
        except Exception as e:
            logger.error(f"Error adding points for user {user_id}: {e}")
            raise

    def get_refer_points(self, user_id: int):
        try:
            user = self.refer_collection.find_one({'user_id': user_id})
            points = user.get('points') if user else 0
            logger.info(f"Points for user {user_id}: {points}")
            return points
        except Exception as e:
            logger.error(f"Error getting points for user {user_id}: {e}")
            raise


# Creating an instance of UserTracker
referdb = UserTracker()
