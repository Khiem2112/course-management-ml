import pandas as pd
import joblib
import sys
from typing import TypedDict, List, Tuple, Any, Dict # Added imports

# --- Configuration and Database Imports ---
from config.config import GLOBAL_CONFIG
from database.execute_service import DBExecuteService as db
from utils.logger import get_class_logger

# Configure logger for this module/class
logger = get_class_logger(__name__, "RecommendationService")

# --- Define the TypedDict for the return value ---
class RecommendationResult(TypedDict):
    """Defines the structure of the recommendation result dictionary."""
    courses: List[str]
    study_method_label: str | None
    engagement_label: str | None
# ---

class RecommendationService:
    """
    Manages loading the ML model, a feature CSV, caching predictions,
    and generating student learning path recommendations.
    """

    # --- Class Attributes for Maps (Load once) ---
    STUDY_METHOD_MAP: Dict[int, str] = {
        0: "Collaborative", 1: "Offline Content", 2: "Interactive",
        3: "Informational", 4: "Resource-Based"
    } #
    ENGAGEMENT_LEVEL_MAP: Dict[int, str] = {
        0: "Moderate Engagement", 1: "High Engagement", 2: "Low Engagement"
    } #
    RECOMMENDATIONS: Dict[int, Dict[int, List[str]]] = {
        # --- Your full RECOMMENDATIONS dictionary here ---
        #
         0: {
            0: ["Interactive AI Basics: Weekly Quizzes and Forums", "Applied AI: Practical Exercises with Peer Feedback", "Introduction to Machine Learning: Online Workshops", "AI Ethics: Case Studies and Discussion Groups"], # Moderate
            1: ["Collaborative AI Projects: Team-Based Learning", "Advanced AI Techniques: Group Workshops and Peer Reviews", "Machine Learning Bootcamp: Intensive Group Projects", "AI in Practice: Team Challenges and Hackathons"], # High
            2: ['Introduction to AI: Self-Paced Fundamentals', 'AI Basics: Introductory Video Series', 'Foundations of Machine Learning: Self-Study Edition', 'AI for Everyone: Introductory Readings and Quizzes'] # Low
        },
        1: { # Offline Content
            0: ["AI Principles: Self-Study with Case Studies", "Machine Learning: Offline Course with Practice Problems", "Applied AI: Textbook and Supplementary Materials", "Data Science: Case Studies and Analytical Exercises"], # Moderate
            1: ["Advanced AI: Comprehensive Textbook with Projects", "Deep Learning: In-Depth Study with Capstone Projects", "AI and Machine learning: Project-Based Learning", "Data Science Mastery: Offline Content with Comprehensive Projects"], # High
            2: ['AI Basics: Essential Readings and Key Concepts', 'Machine Learning Fundamentals: Self-Study Workbook', "AI Concepts: Downloadable Lecture Series", "Introduction to Data Science: Offline Learning Modules"] # Low
        },
         2: { # Interactive
            0: ["Machine Learning: Interactive Coding Exercises", "AI Applications: Interactive Case Studies", "Data Science: Interactive Projects and Peer Reviews", "AI Ethics: Discussion Forums and Interactive Scenarios"], # Moderate
            1: ["Advanced AI: Interactive Group Projects and Hackathons", "Deep Learning: Interactive Labs and Collaborative Projects", "Machine Learning Mastery: Interactive Workshops and Challenges", "AI Research: Collaborative Research Projects and Peer Feedback"], # High
            2: ["AI Basics: Interactive Quizzes and Flashcards", "Introduction to Machine Learning: Interactive Visualizations", "AI Fundamentals: Interactive Notebooks", "AI Concepts: Gamified Learning Modules"] # Low
        },
         3: { # Informational
            0: ["Machine Learning: Structured Video Course", "AI Concepts: Comprehensive Video Series", "Data Science: Interactive Reading and Video Modules", "AI in Practice: Lecture Notes and Case Studies"], # Moderate
            1: ["Advanced AI: Detailed Lecture Series and Readings", "Deep Learning: Advanced Lecture Series with Supplemental Readings", "AI and Machine Learning: Research Papers and Advanced Lectures", "Data Science Masterclass: Comprehensive Reading and Video Content"], # High
            2: ["AI Overview: Short Video Lectures", "Introduction to Machine Learning: Podcast Series", "AI Fundamentals: Infographics and Summaries", "Data Science: Essential Readings and Articles"] # Low
        },
         4: { # Resource-Based
            0: ["Machine Learning: Comprehensive eBooks and Guides", "AI Applications: Case Study Compilations", "Data Science: In-Depth Articles and White Papers", "AI Concepts: Research Articles and Detailed Guides"], # Moderate
            1: ["Advanced AI: Research Papers and Technical Reports", "Deep Learning: Comprehensive Textbooks and Resource Repositories", "Machine Learning Mastery: Advanced Documentation and APIs", "AI Ethics: Government and Institutional Reports"], # High
            2: ["AI Basics: Curated Reading Lists", "Introduction to Machine Learning: Beginner-Friendly Blogs", "Data Science Overview: Quick Reference Guides", "AI Fundamentals: Online Documentation"] # Low
        }
    }


    def __init__(self):
        """
        Initializes the service, loading the model and feature data from
        paths specified in GLOBAL_CONFIG.
        """
        # Type hints for instance attributes
        
        self.model, self.feature_df = self._load_artifacts()

    def _load_artifacts(self) -> Tuple[Any | None, pd.DataFrame | None]:
        """Loads the model and feature DataFrame from disk."""
        model_path: str = GLOBAL_CONFIG.MODEL_PATH
        data_path: str = GLOBAL_CONFIG.FEATURE_DATA_PATH
        
        model: Any | None = None
        feature_df: pd.DataFrame | None = None
        
        # Load Model
        try:
            model = joblib.load(model_path)
            logger.info(f"Successfully loaded prediction model from {model_path}")
        except FileNotFoundError:
            logger.error(f"Error: Model file not found at {model_path}. Prediction disabled.")
        except Exception as e:
            logger.error(f"Error loading model: {e}. Prediction disabled.", exc_info=True)
            
        # Load Feature Data
        try:
            feature_df = pd.read_csv(data_path)
            if 'id_student' in feature_df.columns:
                 # Ensure correct type for matching
                 feature_df['id_student'] = feature_df['id_student'].astype(int)
            logger.info(f"Successfully loaded feature data from {data_path}")
        except FileNotFoundError:
            logger.error(f"Error: Feature data file not found at {data_path}. Prediction disabled.")
        except Exception as e:
            logger.error(f"Error loading feature data: {e}. Prediction disabled.", exc_info=True)

        return model, feature_df


    def _get_cached_recommendation(self, student_id: int) -> Tuple[int | None, int | None]:
        """Checks the studentRecommendations table for existing predictions."""
        logger.debug(f"Checking recommendation cache for student_id: {student_id}")
        cached_result: Dict[str, Any] | None = db.fetch_one(
            "SELECT predicted_study_method, engagement_level FROM studentRecommendations WHERE id_student = %s",
            (student_id,)
        )
        if cached_result:
            logger.info(f"Cache hit for student {student_id}.")
            try:
                # Ensure data from DB is integer
                study_id = int(cached_result['predicted_study_method'])
                engage_id = int(cached_result['engagement_level'])
                return study_id, engage_id
            except (KeyError, TypeError, ValueError) as e:
                logger.warning(f"Cached data for student {student_id} is corrupt: {e}")
                return None, None
        logger.info(f"Cache miss for student {student_id}.")
        return None, None

    def _predict_and_cache(self, student_id: int) -> Tuple[int | None, int | None]:
        """
        Runs prediction using the loaded CSV and caches the result.
        This logic is adapted from your predict.py script.
        """
        # Check if model and data are loaded
        if self.model is None or self.feature_df is None:
             logger.warning("Model or feature data not loaded. Cannot predict.")
             return None, None

        # 1. Get student data row from the loaded DataFrame
        student_data_row: pd.DataFrame = self.feature_df[self.feature_df['id_student'] == student_id]
        
        if student_data_row.empty:
            logger.warning(f"Student {student_id} not found in {GLOBAL_CONFIG.FEATURE_DATA_PATH}.")
            return None, None
        
        student_features: pd.DataFrame = student_data_row.copy()
        
        # 2. Extract Engagement Level (from the CSV data)
        try:
            engagement_level_id: int = int(student_features["engagement_classification"].iloc[0])
        except (KeyError, IndexError, ValueError):
            logger.warning(f"Could not find/parse 'engagement_classification' for student {student_id}.")
            return None, None
            
        # 3. Prepare Features for Prediction (from predict.py)
        cols_to_drop: List[str] = ['id_student', 'study_method_preference', 'final_result']
        existing_cols_to_drop: List[str] = [col for col in cols_to_drop if col in student_features.columns]
        
        student_features = student_features.drop(columns=existing_cols_to_drop)

        # 4. XGBoost Column Name Fix (from predict.py)
        student_features.columns = student_features.columns.astype(str).str.replace('[', '', regex=False) \
                                             .str.replace(']', '', regex=False) \
                                             .str.replace('<', '', regex=False)
        
        # 5. Predict Study Method
        try:
            # model.predict usually returns a numpy array
            predicted_label_array: Any = self.model.predict(student_features)
            study_method_id: int = int(predicted_label_array[0])
        except Exception as e:
            logger.error(f"Error during model prediction for student {student_id}: {e}", exc_info=True)
            return None, None

        # 6. Save to Cache
        self._save_recommendation_to_cache(student_id, study_method_id, engagement_level_id)

        return study_method_id, engagement_level_id

    def _save_recommendation_to_cache(self, student_id: int, study_method_id: int, engagement_level_id: int) -> None:
        """Saves the prediction results to the database cache table."""
        logger.debug(f"Saving prediction to cache: Student={student_id}, Study={study_method_id}, Engagement={engagement_level_id}")
        success: bool | int = db.execute_query(
            """
            INSERT INTO studentRecommendations (id_student, predicted_study_method, engagement_level)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE predicted_study_method = VALUES(predicted_study_method),
                                   engagement_level = VALUES(engagement_level)
            """,
            (student_id, study_method_id, engagement_level_id)
        )
        if not success:
             logger.warning(f"Failed to save prediction to cache for student {student_id}.")


    # --- PUBLIC METHOD (with updated type hints) ---
    def get_recommendations(self, student_id: int) -> RecommendationResult:
        """
        Gets course recommendations for a specific student.

        Checks cache first. If not found, runs prediction using the
        loaded CSV file, caches the result, and then returns recommendations.
        """
        # Ensure student_id is an integer
        try:
            student_id = int(student_id)
        except (ValueError, TypeError):
             logger.error(f"Invalid student_id provided: {student_id}. Must be an integer.")
             # Return matching the TypedDict structure
             return {'courses': ["Invalid student ID provided."], 'study_method_label': None, 'engagement_label': None}

        study_method_id: int | None
        engagement_level_id: int | None
        study_method_id, engagement_level_id = self._get_cached_recommendation(student_id)

        if study_method_id is None or engagement_level_id is None:
            # Not in cache, run prediction
            study_method_id, engagement_level_id = self._predict_and_cache(student_id)

        # Prepare final output, explicitly typing the dictionary
        result: RecommendationResult = {
            'courses': [],
            'study_method_label': None,
            'engagement_label': None
        }

        if study_method_id is None or engagement_level_id is None:
            result['courses'] = ["Could not generate recommendations for this student."]
            return result

        # Lookup courses in the map
        result['courses'] = self.RECOMMENDATIONS.get(study_method_id, {}).get(engagement_level_id, [])
        if not result['courses']:
            result['courses'] = ["No specific recommendations found for this combination."]

        # Add labels
        result['study_method_label'] = self.STUDY_METHOD_MAP.get(study_method_id, f"Unknown ({study_method_id})")
        result['engagement_label'] = self.ENGAGEMENT_LEVEL_MAP.get(engagement_level_id, f"Unknown ({engagement_level_id})")

        logger.info(f"Final recommendations for Student {student_id}: Study={result['study_method_label']}, Engagement={result['engagement_label']}")
        return result