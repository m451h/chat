"""
Mock backend functions to simulate EHR system data fetching
"""
from typing import List, Dict, Optional


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """
    Mock function to fetch user data from EHR system
    In production, this would call actual EHR API
    
    Args:
        user_id: 13-digit user ID
    
    Returns:
        User data dictionary or None
    """
    # Mock data - in production, this would fetch from actual EHR
    mock_users = {
        1234567890123: {
            "id": 1234567890123,
            "name": "علی احمدی",
            "age": 52,
            "gender": "male"
        },
        9876543210987: {
            "id": 9876543210987,
            "name": "فاطمه محمدی",
            "age": 58,
            "gender": "female"
        },
        1111222233334: {
            "id": 1111222233334,
            "name": "حسین رضایی",
            "age": 35,
            "gender": "male"
        }
    }
    
    return mock_users.get(user_id)


def get_user_conditions(user_id: int) -> List[Dict]:
    """
    Mock function to fetch user's diagnosed conditions from EHR system
    
    Args:
        user_id: 13-digit user ID
    
    Returns:
        List of condition dictionaries
    """
    # Mock data - in production, this would fetch from actual EHR
    mock_conditions = {
        1234567890123: [
            {
                "name": "دیابت نوع دو",
                "name_en": "diabetes_type2",
                "data_file": "diabetes_type2.json",
                "diagnosed_date": "1400/05/15"
            },
            {
                "name": "فشار خون بالا",
                "name_en": "hypertension",
                "data_file": "hypertension.json",
                "diagnosed_date": "1398/03/20"
            }
        ],
        9876543210987: [
            {
                "name": "فشار خون بالا",
                "name_en": "hypertension",
                "data_file": "hypertension.json",
                "diagnosed_date": "1397/08/10"
            }
        ],
        1111222233334: [
            {
                "name": "آسم",
                "name_en": "asthma",
                "data_file": "asthma.json",
                "diagnosed_date": "1388/02/05"
            }
        ]
    }
    
    return mock_conditions.get(user_id, [])


def fetch_condition_data(user_id: int, condition_name_en: str) -> Optional[Dict]:
    """
    Mock function to fetch specific condition data for a user
    
    Args:
        user_id: 13-digit user ID
        condition_name_en: English name of condition
    
    Returns:
        Condition data dictionary or None
    """
    # In production, this would fetch personalized data from EHR
    # For now, we just return the data file path
    conditions = get_user_conditions(user_id)
    
    for condition in conditions:
        if condition['name_en'] == condition_name_en:
            return condition
    
    return None
