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
    
    CLUSTER_NAME_MAP = {
    0: "Resource-Based Learners",
    1: "Balanced Achievers",
    2: "High-Achieving Collaborators",
    3: "Independent Explorers",
    4: "Interactive Specialists",
    5: "Offline Achievers", 
    6: "Engaged Collaborators"
  }

    # --- The Master 5x7 -> 5x3 Recommendation Map ---
    RECOMMENDATIONS_CONTENT = {
        COLLABORATIVE: { # Archetypes 1.1, 2.2, 3.1
            ENGAGEMENT_HIGH: [ # 1.1 The Collaborative Leader
                "We've noticed you're a leader in the forums, which is fantastic.",
                "**Action:** Can you help elevate the discussion? Try starting a thread that summarizes the 'Top 3 Takeaways' from this week's module, or pose a question that connects this topic to a previous one."
            ],
            ENGAGEMENT_MEDIUM: [ # 2.2 The Quiet Observer
                "We see you're actively reading the forums, which is a great way to learn. We'd love to hear your perspective too.",
                "**Action:** A great first step is to use the 'Like' button on posts you find helpful, or try answering a simple poll. The next step? Ask one question you have in the 'Weekly Questions' thread."
            ],
            ENGAGEMENT_LOW: [ # 3.1 The Hesitant Lurker
                "It can be intimidating to post in a public forum. Many students feel the same way.",
                "**Action:** You don't need to post publicly. If you have a question, feel free to reply to this message directly. We are here to help."
            ]
        },
        OFFLINE_CONTENT: { # Archetypes 1.2, 2.1, 3.2
            ENGAGEMENT_HIGH: [ # 1.2 The Diligent Researcher
                "Your pace is excellent and you're mastering the core materials. You're ready for more complex work.",
                "**Action:** We've unlocked an 'Extension' module for you. It contains links to academic papers and industry case studies that go far beyond the syllabus."
            ],
            ENGAGEMENT_MEDIUM: [ # 2.1 The Steady Worker
                "Great job staying on schedule this month. Your consistency is noted and is the key to success.",
                "**Action:** As you review this week's chapter, pay special attention to the 'Key Terms' box on page 4. It's a hint for the upcoming quiz."
            ],
            ENGAGEMENT_LOW: [ # 3.2 The Overwhelmed Novice
                "It's easy to feel overwhelmed by the syllabus. Let's simplify and remove the clutter.",
                "**Action:** Ignore the full list of readings for now. Your *only* goal today is to read the 2-page 'Module Summary' PDF. That's it. (We've linked it here)."
            ]
        },
        INTERACTIVE: { # Archetypes 1.3, 2.3, 3.3
            ENGAGEMENT_HIGH: [ # 1.3 The Skilled Achiever
                "You've aced the last two labs, which is outstanding. You're ready to move from consuming content to creating it.",
                "**Action:** We have a beta version of an 'Advanced Scenario' for this lab. Would you be willing to test it out and give us feedback?"
            ],
            ENGAGEMENT_MEDIUM: [ # 2.3 The Efficient Practitioner
                "We see you're focusing on the quizzes to stay efficient. That's smart, but you might be missing the 'why' behind the 'how.'",
                "**Action:** Here's a hint: The answer to the final, 10-point question on this week's quiz is discussed in detail in the 'Optional Reading' PDF. It's a good return on investment."
            ],
            ENGAGEMENT_LOW: [ # 3.3 The Anxious Performer
                "We noticed you spent a lot of time on the last quiz. It's okay to struggle; that's part of learning.",
                "**Action:** To help reduce the pressure, we've opened an 'Untimed Practice Mode' for this quiz. You can take it as many times as you want, with no stakes, to get comfortable with the material."
            ]
        },
        INFORMATIONAL: { # Archetypes (1.2/1.3 hybrid), 2.2, 3.2
            ENGAGEMENT_HIGH: [ # (Adapted from 1.2/1.3)
                "You've watched all the core lectures. Your high engagement shows you're ready for a deeper dive.",
                "**Action:** We've made a 'Guest Lecture' from an industry expert available to you. It connects this week's topic to a real-world case study at a major company."
            ],
            ENGAGEMENT_MEDIUM: [ # 2.2 The Quiet Observer
                "We see you're diligently watching the videos, which is great. You're absorbing the material, but the next step is to synthesize it.",
                "**Action:** This week, try a 'low-stakes' interaction. We're running a 1-click poll: 'What was the hardest part of this video?' Just click one option. It helps you reflect and helps us improve."
            ],
            ENGAGEMENT_LOW: [ # 3.2 The Overwhelmed Novice
                "It's easy to feel overwhelmed by a list of 1-hour lectures. Let's start with a pebble, not the mountain.",
                "**Action:** Ignore the full lecture list for now. Your *only* goal today is to watch this 5-minute 'Module Introduction' video. That's it."
            ]
        },
        RESOURCE_BASED: { # Archetypes 1.2, (2.1 hybrid), (3.2 hybrid)
            ENGAGEMENT_HIGH: [ # 1.2 The Diligent Researcher
                "Your high engagement with all the course resources (e-books, articles) shows you're a voracious consumer.",
                "**Action:** We've unlocked a 'Deep Dive' folder for you with advanced, optional materials. We are *not* giving you more work; we are giving you more *complex* work."
            ],
            ENGAGEMENT_MEDIUM: [ # (Adapted from 2.1)
                "Great job exploring the different resources. That curiosity is key.",
                "**Action:** To help you focus, try to use the 'Quick Reference Guide' as a 'cheat sheet' while you're working on the main assignment. It connects all the resources together."
            ],
            ENGAGEMENT_LOW: [ # (Adapted from 3.2)
                "It's easy to feel lost in all the files and folders. Let's make it simple.",
                "**Action:** Ignore all the optional folders. For this week, find and read *only* the one file named 'Module_1_Getting_Started.pdf'. It's the perfect place to start."
            ]
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
        query = "SELECT id_student, name_student, study_method_id, cluster_id FROM studentInfo WHERE id_student = %s"
        
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
        logger.info(f'Full data: {student_data}')
        if not student_data:
            logger.warning(f"No data found for student_id: {student_id}")
            return {"status": "error", "message": "Student not found."} 

        # --- 3. Process the Data ---
        # --- 3. Process the Data & Handle Missing Values ---
        method_id = student_data.get('study_method_id')
        cluster_id = student_data.get('cluster_id')

        # STRATEGY: Default Fallback
        # If data is missing, assume "General" or "New" student profile.
        is_generic_recommendation = False
        
        if method_id is None:
            logger.warning(f"Student {student_id} missing study_method_id. Using default (0).")
            method_id = 0 # Default to 'Collaborative' or your most common type
            is_generic_recommendation = True
            
        if cluster_id is None:
            logger.warning(f"Student {student_id} missing cluster_id. Using default (0).")
            cluster_id = 0 # Default to Cluster 0
            is_generic_recommendation = True

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
        result['cluster_name'] = self.CLUSTER_NAME_MAP.get(cluster_id, "Unknown")
        return result   

