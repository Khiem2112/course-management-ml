import sqlite3
import pandas as pd
from typing import List, Dict, Tuple, Any
from database.execute_service import DBExecuteService as db
from mysql.connector import Error as DBError

from utils.logger import get_class_logger

# --- 1. The Recommendation Class ---

logger = get_class_logger(__name__, "RecommendationManager")

class RecommendationManager:
    """
    Manages the 5 (Study Method) x 7 (Cluster) recommendation map.

    This class performs a crucial mapping: it translates the 7 raw cluster
    IDs into the 3 "Engagement Levels" (Low, Medium, High) that your
    recommendation content is based on.
    """

    # --- Define clear constants for your 5 Study Methods ---
    COLLABORATIVE = 0
    OFFLINE_CONTENT = 1
    INTERACTIVE = 2
    INFORMATIONAL = 3
    RESOURCE_BASED = 4

    # --- Define the 3 Engagement Levels from your old map ---
    ENGAGEMENT_MEDIUM = 0
    ENGAGEMENT_HIGH = 1
    ENGAGEMENT_LOW = 2

    # --- The Master 5x7 -> 5x3 Recommendation Map ---
    RECOMMENDATIONS_CONTENT = {
        COLLABORATIVE: {
            ENGAGEMENT_MEDIUM: ["Interactive AI Basics: Weekly Quizzes and Forums", "Applied AI: Practical Exercises with Peer Feedback"],
            ENGAGEMENT_HIGH: ["Collaborative AI Projects: Team-Based Learning", "Advanced AI Techniques: Group Workshops"],
            ENGAGEMENT_LOW: ['Introduction to AI: Self-Paced Fundamentals', 'AI Basics: Introductory Video Series']
        },
        OFFLINE_CONTENT: {
            ENGAGEMENT_MEDIUM: ["AI Principles: Self-Study with Case Studies", "Machine Learning: Offline Course with Practice Problems"],
            ENGAGEMENT_HIGH: ["Advanced AI: Comprehensive Textbook with Projects", "Deep Learning: In-Depth Study with Capstone Projects"],
            ENGAGEMENT_LOW: ['AI Basics: Essential Readings and Key Concepts', 'Machine Learning Fundamentals: Self-Study Workbook']
        },
        INTERACTIVE: {
            ENGAGEMENT_MEDIUM: ["Machine Learning: Interactive Coding Exercises", "AI Applications: Interactive Case Studies"],
            ENGAGEMENT_HIGH: ["Advanced AI: Interactive Group Projects and Hackathons", "Deep Learning: Interactive Labs"],
            ENGAGEMENT_LOW: ["AI Basics: Interactive Quizzes and Flashcards", "Introduction to Machine Learning: Interactive Visualizations"]
        },
        INFORMATIONAL: {
            ENGAGEMENT_MEDIUM: ["Machine Learning: Structured Video Course", "AI Concepts: Comprehensive Video Series"],
            ENGAGEMENT_HIGH: ["Advanced AI: Detailed Lecture Series and Readings", "Deep Learning: Advanced Lecture Series"],
            ENGAGEMENT_LOW: ["AI Overview: Short Video Lectures", "Introduction to Machine Learning: Podcast Series"]
        },
        RESOURCE_BASED: {
            ENGAGEMENT_MEDIUM: ["Machine Learning: Comprehensive eBooks and Guides", "AI Applications: Case Study Compilations"],
            ENGAGEMENT_HIGH: ["Advanced AI: Research Papers and Technical Reports", "Deep Learning: Comprehensive Textbooks"],
            ENGAGEMENT_LOW: ["AI Basics: Curated Reading Lists", "Introduction to Machine Learning: Beginner-Friendly Blogs"]
        }
    }

    # --- Metadata maps for clear, human-readable output ---
    STUDY_METHOD_NAMES = {
        COLLABORATIVE: "Collaborative",
        OFFLINE_CONTENT: "Offline Content",
        INTERACTIVE: "Interactive",
        INFORMATIONAL: "Informational",
        RESOURCE_BASED: "Resource-Based"
    }

    ENGAGEMENT_LEVEL_NAMES = {
        ENGAGEMENT_HIGH: "High Engagement",
        ENGAGEMENT_MEDIUM: "Medium Engagement",
        ENGAGEMENT_LOW: "Low Engagement / At-Risk"
    }

    def __init__(self):
        # In a real app, you might load this map from a JSON or YAML file.
        print("RecommendationManager initialized.")

    def _map_cluster_to_engagement(self, cluster_id: int) -> int:
        """
        **This is the core logic that connects your 7 clusters to your 3 levels.**

        This is a HYPOTHETICAL mapping. You must replace this with your
        actual analysis from your clustering notebook
        (e.g., by checking the `cluster_centers_`).
        """
        # Example mapping:
        if cluster_id in [5, 6]:
            # Clusters 5 & 6 have the highest click counts
            return self.ENGAGEMENT_HIGH
        elif cluster_id in [2, 3, 4]:
            # Clusters 2, 3, 4 are the "average" students
            return self.ENGAGEMENT_MEDIUM
        elif cluster_id in [0, 1]:
            # Clusters 0 & 1 have the lowest scores and clicks
            return self.ENGAGEMENT_LOW
        else:
            # Fallback for safety
            print(f"Warning: Unknown cluster_id {cluster_id}. Defaulting to Low Engagement.")
            return self.ENGAGEMENT_LOW

    def get_recommendation(self, study_method_id: int, cluster_id: int) -> Dict[str, Any]:
        """
        Gets the recommendations and metadata for a given student's IDs.
        """
        # 1. Map the raw cluster ID to a meaningful engagement level
        engagement_level_id = self._map_cluster_to_engagement(cluster_id)

        # 2. Look up the content in the master map
        try:
            # Find the study method "bucket"
            method_bucket = self.RECOMMENDATIONS_CONTENT.get(study_method_id)
            if not method_bucket:
                raise KeyError(f"Invalid study_method_id: {study_method_id}")

            # Find the recommendations within that bucket
            recommendations = method_bucket.get(engagement_level_id)
            if not recommendations:
                raise KeyError(f"Invalid engagement_level_id: {engagement_level_id}")

            # 3. Get human-readable names
            method_name = self.STUDY_METHOD_NAMES.get(study_method_id, "Unknown")
            engagement_name = self.ENGAGEMENT_LEVEL_NAMES.get(engagement_level_id, "Unknown")

            return {
                "status": "success",
                "study_method_name": method_name,
                "engagement_level_name": engagement_name,
                "recommendations": recommendations,
                "raw_ids": {
                    "study_method_id": study_method_id,
                    "cluster_id": cluster_id,
                    "mapped_engagement_id": engagement_level_id
                }
            }
        except KeyError as e:
            return {
                "status": "error",
                "message": str(e),
                "recommendations": [],
                "raw_ids": {
                    "study_method_id": study_method_id,
                    "cluster_id": cluster_id
                }
            }
    def get_recommendation_for_student(self, student_id: int) -> dict:
        """
        Fetches a single student's pre-computed IDs from the database,
        gets their recommendation from the manager, and returns the result.

        This is the primary function your application (e.g., PyQt6) will call.

        Args:
            student_id (int): The ID of the student to look up.
            manager (RecommendationManager): An initialized instance of the manager.

        Returns:
            dict: A dictionary containing the recommendation result or error info.
        """
        logger.info(f"Processing request for student_id: {student_id}")

        # --- 1. Fetch Data (The "Fast" Query) ---
        # Use %s for parameter binding as per mysql.connector standard
        query = "SELECT study_method_id, cluster_id FROM studentInfo WHERE id_student = %s"
        params = (student_id,)

        student_data = None
        try:
            # Use fetch_one, which is more appropriate for a single lookup
            student_data = db.fetch_one(query, params)
        except DBError as e:
            logger.error(f"Database query failed for student {student_id}: {e}")
            return {"status": "error", "message": f"Database error. Check connection."}
        except Exception as e:
            logger.error(f"An unexpected error occurred during data fetching for {student_id}: {e}")
            return {"status": "error", "message": f"Unexpected application error."}

        # --- 2. Handle "Not Found" ---
        if not student_data:
            logger.warning(f"No data found for student_id: {student_id}")
            return {"status": "error", "message": "Student not found."}

        # --- 3. Process the Data ---
        method_id = student_data.get('study_method_id')
        cluster_id = student_data.get('cluster_id')

        # --- CRITICAL: Handle NULL/None Data ---
        # (As seen for student 30268 in your demo_tabe_student_info.csv)
        if method_id is None or cluster_id is None:
            logger.warning(f"Student {student_id} has missing (NULL) data.")
            return {
                "status": "error",
                "message": "Recommendation cannot be generated. Student has incomplete data."
            }

        try:
            # Ensure data is integer before passing to manager
            method_id = int(method_id)
            cluster_id = int(cluster_id)
        except ValueError:
            logger.error(f"Data is corrupt for student {student_id}. "
                        f"Got: method={method_id}, cluster={cluster_id}")
            return {
                "status": "error",
                "message": "Data is corrupt. Cannot process recommendation."
            }

        # --- 4. Get the recommendation ---
        # This is the final step, mapping the IDs to the content.
        result = self.get_recommendation(method_id, cluster_id)
        return result

