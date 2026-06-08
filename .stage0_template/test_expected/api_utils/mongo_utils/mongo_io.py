"""
MongoDB I/O utilities module for api_utils.

This module provides a singleton MongoIO class that manages MongoDB connections
and provides a high-level interface for common database operations including
CRUD operations (create, read, update, delete) and document queries.
"""
import sys
from bson import ObjectId 
from pymongo import MongoClient, ASCENDING, DESCENDING
from api_utils.config.config import Config

import logging
logger = logging.getLogger(__name__)

# TODO: - Refactor to use connection pooling

class MongoIO:
    """
    Singleton MongoDB I/O manager for the application.
    
    The MongoIO class provides a centralized interface for all MongoDB operations,
    managing a single connection to the database throughout the application lifecycle.
    It uses the singleton pattern to ensure only one connection is maintained.
    
    The class automatically connects to MongoDB on first instantiation using
    configuration from the Config singleton. Connection settings include:
    - Connection string from MONGO_CONNECTION_STRING
    - Database name from MONGO_DB_NAME
    - Server selection timeout: 2000ms
    - Socket timeout: 5000ms
    
    All methods require an active connection and will raise exceptions if called
    when disconnected. Collections are automatically created if they don't exist
    when accessed.
    
    Attributes:
        _instance (MongoIO): The singleton instance of the MongoIO class.
        config (Config): Reference to the Config singleton instance.
        client (MongoClient): The PyMongo client instance.
        db (Database): The MongoDB database instance.
        connected (bool): Connection status flag.
    
    Example:
        >>> mongo = MongoIO.get_instance()
        >>> doc_id = mongo.create_document("users", {"name": "John"})
        >>> user = mongo.get_document("users", doc_id)
        >>> mongo.disconnect()
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create or return the singleton instance of MongoIO.
        
        On first call, this method:
        - Creates the singleton instance
        - Initializes MongoDB connection using Config settings
        - Performs a ping to verify connectivity
        - Sets up the database reference
        
        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.
        
        Returns:
            MongoIO: The singleton MongoIO instance.
        
        Note:
            This method should not be called directly. Use get_instance() instead.
        """
        if cls._instance is None:
            cls._instance = super(MongoIO, cls).__new__(cls, *args, **kwargs)
            
            
            # TODO: Add timeout configs to Client and use here in client constructor
            config = Config.get_instance()
            client = MongoClient(
                config.MONGO_CONNECTION_STRING, 
                serverSelectionTimeoutMS=2000, 
                socketTimeoutMS=5000
            )
            client.admin.command('ping')  # Force connection

            cls._instance.config = config
            cls._instance.client = client
            cls._instance.db = client.get_database(config.MONGO_DB_NAME)
            cls._instance.connected = True
            logger.info(f"Connected to MongoDB")
        return cls._instance

    def disconnect(self):
        """
        Disconnect from MongoDB and close the client connection.
        
        This method closes the MongoDB client connection and sets the connected
        flag to False. If disconnection fails, the application will exit with
        status code 1 (fail-fast behavior).
        
        Raises:
            Exception: If called when not connected.
            SystemExit: If disconnection fails (exit code 1).
        """
        if not self.connected: raise Exception("disconnect when mongo not connected")
            
        try:
            if self.client:
                self.client.close()
                logger.info("Disconnected from MongoDB")
        except Exception as e:
            logger.fatal(f"Failed to disconnect from MongoDB: {e} - exiting")
            sys.exit(1) # fail fast 

    def get_collection(self, collection_name):
        """Get a collection, creating it if it doesn't exist.
        
        Args:
            collection_name (str): Name of the collection to get/create
            
        Returns:
            Collection: The MongoDB collection object
        """
        if not self.connected: raise Exception("get_collection when Mongo Not Connected")
        
        try:
            # Check if collection exists
            if collection_name not in self.db.list_collection_names():
                # Create collection if it doesn't exist
                self.db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
            
            return self.db.get_collection(collection_name)
        except Exception as e:
            logger.error(f"Failed to get/create collection: {collection_name} {e}")
            raise e

    def drop_collection(self, collection_name):
        """Drop a collection from the database.
        
        Args:
            collection_name (str): Name of the collection to drop
            
        Returns:
            bool: True if collection was dropped, False if it didn't exist
        """
        if not self.connected: raise Exception("drop_collection when Mongo Not Connected")

        try:
            if collection_name in self.db.list_collection_names():
                self.db.drop_collection(collection_name)
                logger.info(f"Dropped collection: {collection_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to drop collection: {e}")
            raise e
      
    def get_documents(self, collection_name, match=None, project=None, sort_by=None):
        """
        Retrieve a list of documents based on a match, projection, and optional sorting.

        Args:
            collection_name (str): Name of the collection to query.
            match (dict, optional): MongoDB match filter. Defaults to {}.
            project (dict, optional): Fields to include or exclude. Defaults to None.
            sort_by (list of tuple, optional): Sorting criteria (e.g., [('field1', ASCENDING), ('field2', DESCENDING)]). Defaults to None.

        Returns:
            list: List of documents matching the query.
        """
        if not self.connected: raise Exception("get_documents when Mongo Not Connected")

        # Default match and projection
        match = match or {}
        project = project or None
        sort_by = sort_by or None
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(match, project)
            if sort_by: cursor = cursor.sort(sort_by)

            documents = list(cursor)
            return documents
        except Exception as e:
            logger.error(f"Failed to get documents from collection '{collection_name}': {e}")
            raise e
                
    def update_document(self, collection_name, document_id=None, match=None, set_data=None, push_data=None, add_to_set_data=None, pull_data=None):
        """
        Update a document in the specified collection with optional set, push, add_to_set, and pull operations.

        This method supports multiple MongoDB update operations:
        - $set: Update or set field values
        - $push: Append items to arrays
        - $addToSet: Add unique items to arrays
        - $pull: Remove items from arrays

        Either document_id or match must be provided to identify the document.
        If document_id is provided, it will be converted to ObjectId and used
        as the match criteria.

        Args:
            collection_name (str): Name of the collection to update.
            document_id (str, optional): ID of the document to update. If provided,
                match will be set to {"_id": ObjectId(document_id)}.
            match (dict, optional): Custom match criteria for finding the document.
                Ignored if document_id is provided. Defaults to None.
            set_data (dict, optional): Fields to update or set using $set operator.
                Defaults to None.
            push_data (dict, optional): Fields to push items into arrays using $push.
                Defaults to None.
            add_to_set_data (dict, optional): Fields to add unique items to arrays
                using $addToSet. Defaults to None.
            pull_data (dict, optional): Fields to remove items from arrays using $pull.
                Defaults to None.

        Returns:
            dict: The updated document if successful, None if document not found.

        Raises:
            Exception: If not connected, if neither document_id nor match is provided,
                or if the operation fails.
        """
        if not self.connected: raise Exception("update_document when Mongo Not Connected")

        try:
            document_collection = self.get_collection(collection_name)

            if match is None: 
                document_object_id = ObjectId(document_id)
                match = {"_id": document_object_id}

            # Build the update pipeline
            pipeline = {}
            if set_data:
                pipeline["$set"] = set_data
            if push_data:
                pipeline["$push"] = push_data
            if add_to_set_data:
                pipeline["$addToSet"] = add_to_set_data
            if pull_data:
                pipeline["$pull"] = pull_data

            updated = document_collection.find_one_and_update(match, pipeline, return_document=True)

        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            raise

        return updated

    def get_document(self, collection_name, document_id):
        """
        Retrieve a single document by its ID.
        
        Args:
            collection_name (str): Name of the collection to query.
            document_id (str): The document ID as a string (will be converted to ObjectId).
        
        Returns:
            dict or None: The document if found, None otherwise.
        
        Raises:
            Exception: If not connected or if the operation fails.
        """
        if not self.connected: raise Exception("get_document when Mongo Not Connected")

        try:
            # Get the document
            collection = self.get_collection(collection_name)
            document_object_id = ObjectId(document_id)
            document = collection.find_one({"_id": document_object_id})
            return document
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            raise e 

    def create_document(self, collection_name, document):
        """
        Create a new document in the specified collection.
        
        Args:
            collection_name (str): Name of the collection to insert into.
            document (dict): The document data to insert.
        
        Returns:
            str: The string representation of the inserted document's _id.
        
        Raises:
            Exception: If not connected or if the operation fails.
        """
        if not self.connected: raise Exception("create_document when Mongo Not Connected")
        
        try:
            document_collection = self.get_collection(collection_name)
            result = document_collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise e

    def upsert_document(self, collection_name, match, data):
        """Upsert a document - create if not exists, update if exists.
        
        Args:
            collection_name (str): Name of the collection
            match (dict): Match criteria to find existing document
            data (dict): Data to insert or update
            
        Returns:
            dict: The upserted document
        """
        if not self.connected: raise Exception("upsert_document when Mongo Not Connected")
        
        try:
            collection = self.get_collection(collection_name)
            result = collection.find_one_and_update(
                match,
                {"$set": data},
                upsert=True,
                return_document=True
            )
            return result
        except Exception as e:
            logger.error(f"Failed to upsert document: {e}")
            raise e

    @staticmethod
    def get_instance():
        """
        Get the singleton instance of the MongoIO class.
        
        This is the preferred way to access the MongoIO instance. If no instance
        exists, one will be created automatically, which will establish a connection
        to MongoDB using configuration from the Config singleton.
        
        Returns:
            MongoIO: The singleton MongoIO instance.
        
        Example:
            >>> mongo = MongoIO.get_instance()
            >>> doc_id = mongo.create_document("users", {"name": "Alice"})
            >>> mongo.disconnect()
        """
        if MongoIO._instance is None:
            MongoIO()
        return MongoIO._instance

