from typing import List, Dict, Any, Optional
import logging
import uuid
import json
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorStore:
    """In-memory vector store with JSON file persistence for storing automotive generations."""
    
    def __init__(self, persist_dir: str = "./chroma_data"):
        self.persist_dir = persist_dir
        self.collections: Dict[str, List[Dict]] = {}
        self._ensure_persist_dir()
    
    def _ensure_persist_dir(self):
        """Create persist directory if it doesn't exist."""
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, collection_name: str) -> str:
        """Get the file path for a collection's data."""
        # Sanitize collection name for filename
        safe_name = "".join(c for c in collection_name if c.isalnum() or c in "_-")
        return os.path.join(self.persist_dir, f"{safe_name}.json")
    
    def _load_collection(self, collection_name: str) -> List[Dict]:
        """Load collection from file if it exists."""
        file_path = self._get_file_path(collection_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading collection {collection_name}: {e}")
        return []
    
    def _save_collection(self, collection_name: str):
        """Save collection to file."""
        file_path = self._get_file_path(collection_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.collections.get(collection_name, []), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving collection {collection_name}: {e}")
    
    def get_or_create_collection(self, name: str) -> str:
        """Get or create a collection for storing embeddings."""
        if name not in self.collections:
            self.collections[name] = self._load_collection(name)
        return name
    
    def add_generation(self, collection_name: str, prompt: str, narrative: str, 
                       image_url: str, metadata: Optional[Dict] = None) -> str:
        """
        Add a generation record to the vector store.
        
        Args:
            collection_name: Name of the collection
            prompt: The original prompt
            narrative: The generated narrative
            image_url: URL of the generated image
            metadata: Additional metadata
            
        Returns:
            ID of the inserted record
        """
        try:
            # Ensure collection exists
            self.get_or_create_collection(collection_name)
            
            # Generate a unique ID
            record_id = str(uuid.uuid4())
            
            # Create document combining prompt and narrative
            document = f"Prompt: {prompt}\n\nNarrative: {narrative}"
            
            # Prepare metadata
            meta = metadata or {}
            meta.update({
                "prompt": prompt,
                "narrative": narrative[:500] if narrative else "",  # Limit length for metadata
                "image_url": image_url,
                "created_at": datetime.now().isoformat()
            })
            
            # Create record
            record = {
                "id": record_id,
                "document": document,
                "metadata": meta
            }
            
            # Add to collection
            self.collections[collection_name].append(record)
            
            # Save to file
            self._save_collection(collection_name)
            
            logger.info(f"Added generation record: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error adding generation: {str(e)}")
            raise
    
    def search_similar(self, collection_name: str, query: str, 
                       n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar generations based on a query.
        Uses simple text matching for now.
        
        Args:
            collection_name: Name of the collection
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of similar records with their metadata
        """
        try:
            # Ensure collection exists
            self.get_or_create_collection(collection_name)
            
            records = self.collections.get(collection_name, [])
            
            if not records:
                return []
            
            # Simple text-based scoring (in production, use proper embeddings)
            query_lower = query.lower()
            scored_records = []
            
            for record in records:
                doc_lower = record.get("document", "").lower()
                # Calculate simple similarity score
                score = 0
                
                # Check if query terms appear in document
                query_terms = query_lower.split()
                for term in query_terms:
                    if term in doc_lower:
                        score += 1
                
                # Add to results with distance (inverse of score)
                if score > 0:
                    scored_records.append({
                        "id": record["id"],
                        "document": record.get("document"),
                        "metadata": record.get("metadata"),
                        "distance": 1.0 / (1.0 + score)  # Lower is more similar
                    })
            
            # Sort by distance (lower is more similar)
            scored_records.sort(key=lambda x: x["distance"])
            
            return scored_records[:n_results]
            
        except Exception as e:
            logger.error(f"Error searching similar: {str(e)}")
            return []
    
    def get_history(self, collection_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get generation history.
        
        Args:
            collection_name: Name of the collection
            limit: Maximum number of records to return
            
        Returns:
            List of generation records
        """
        try:
            # Ensure collection exists
            self.get_or_create_collection(collection_name)
            
            records = self.collections.get(collection_name, [])
            
            if not records:
                return []
            
            # Sort by created_at descending
            sorted_records = sorted(
                records,
                key=lambda x: x.get("metadata", {}).get("created_at", ""),
                reverse=True
            )
            
            # Format output
            history = []
            for record in sorted_records[:limit]:
                history.append({
                    "id": record["id"],
                    "metadata": record.get("metadata", {}),
                    "document": record.get("document")
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            return []
    
    def delete_record(self, collection_name: str, record_id: str) -> bool:
        """
        Delete a record from the collection.
        
        Args:
            collection_name: Name of the collection
            record_id: ID of the record to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            records = self.collections.get(collection_name, [])
            
            # Find and remove record
            new_records = [r for r in records if r.get("id") != record_id]
            
            if len(new_records) < len(records):
                self.collections[collection_name] = new_records
                self._save_collection(collection_name)
                logger.info(f"Deleted record: {record_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting record: {str(e)}")
            return False
    
    def clear_collection(self, collection_name: str) -> bool:
        """
        Clear all records from a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if collection_name in self.collections:
                self.collections[collection_name] = []
                self._save_collection(collection_name)
                logger.info(f"Cleared collection: {collection_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
