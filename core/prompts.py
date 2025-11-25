"""
Persian prompt templates for medical chatbot
"""
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def _extract_doctor_guide(condition_data: dict) -> str:
    """
    Extract doctor guide/note from condition_data
    
    Args:
        condition_data: Dictionary with patient data
    
    Returns:
        Doctor guide text or empty string
    """
    if not condition_data:
        return ""
    
    # Check for common keys that might contain doctor guide
    possible_keys = ["doctor_guide", "doctor_note", "guide", "doctor_instructions", 
                     "medical_guide", "treatment_guide", "plan_guide"]
    
    for key in possible_keys:
        if key in condition_data:
            value = condition_data[key]
            if value:
                # If it's a string, return it directly
                if isinstance(value, str):
                    return value
                # If it's a dict or list, convert to string
                elif isinstance(value, (dict, list)):
                    return json.dumps(value, ensure_ascii=False)
                else:
                    return str(value)
    
    return ""


def _format_condition_data(condition_data: dict, exclude_keys: list = None) -> str:
    """
    Safely format condition_data to string, handling nested structures
    
    Args:
        condition_data: Dictionary with patient data (may contain nested dicts/lists)
        exclude_keys: List of keys to exclude from formatting (e.g., doctor_guide)
    
    Returns:
        Formatted string representation
    """
    if not condition_data:
        return ""
    
    if exclude_keys is None:
        exclude_keys = []
    
    def format_value(key, value, indent=0):
        """Recursively format nested values"""
        prefix = "  " * indent
        if isinstance(value, dict):
            lines = [f"{prefix}- {key}:"]
            for k, v in value.items():
                lines.extend(format_value(k, v, indent + 1))
            return lines
        elif isinstance(value, list):
            lines = [f"{prefix}- {key}:"]
            for i, item in enumerate(value):
                if isinstance(item, (dict, list)):
                    lines.extend(format_value(f"[{i}]", item, indent + 1))
                else:
                    lines.append(f"{prefix}  - {item}")
            return lines
        else:
            return [f"{prefix}- {key}: {value}"]
    
    lines = []
    for key, value in condition_data.items():
        # Skip excluded keys (like doctor_guide which is shown separately)
        if key in exclude_keys:
            continue
        try:
            if isinstance(value, (dict, list)):
                # Use recursive formatting for nested structures
                formatted = format_value(key, value)
                lines.extend(formatted)
            else:
                lines.append(f"- {key}: {value}")
        except Exception as e:
            # Fallback: just convert to string
            lines.append(f"- {key}: {str(value)}")
    
    return "\n".join(lines)


def get_educational_prompt(treatment_plan_name: str, condition_data: dict) -> str:
    """
    Generate initial educational content prompt in Persian
    
    Args:
        treatment_plan_name: Name of the treatment plan in Persian
        condition_data: User-specific data about the condition
    
    Returns:
        Formatted prompt string
    """
    # Extract doctor guide separately
    doctor_guide = _extract_doctor_guide(condition_data)
    
    # Format patient data excluding doctor guide keys
    exclude_keys = ["doctor_guide", "doctor_note", "guide", "doctor_instructions", 
                    "medical_guide", "treatment_guide", "plan_guide"]
    data_str = _format_condition_data(condition_data, exclude_keys=exclude_keys)
    
    # Build prompt with doctor guide section if available
    doctor_guide_section = ""
    if doctor_guide:
        doctor_guide_section = f"""

راهنمای پزشک برای این برنامه درمانی:
{doctor_guide}

این راهنمای پزشک بسیار مهم است و باید در تمام پاسخ‌های شما به عنوان مرجع اصلی در نظر گرفته شود. لطفاً مطمئن شوید که تمام توصیه‌ها و نکات ذکر شده در راهنمای پزشک را در پاسخ خود لحاظ کنید."""
    
    prompt = f"""شما یک دستیار پزشکی هوشمند و آموزشی هستید که به زبان فارسی با بیماران صحبت می‌کنید.

بیمار با برنامه درمانی "{treatment_plan_name}" مراجعه کرده است.
{doctor_guide_section}

اطلاعات شخصی بیمار:
{data_str if data_str else "(اطلاعات اضافی موجود نیست)"}

لطفا یک یادداشت آموزشی جامع و شخصی‌سازی شده درباره این برنامه درمانی بنویسید که با توجه به داده‌های بالینی بیمار و راهنمای پزشک باشد.
لطفاً یک متن آموزشی جامع و شخصی‌سازی شده درباره این برنامه درمانی برای این بیمار بنویسید که شامل موارد زیر باشد:

بخش اول: اطلاعات کلی و مهم درباره برنامه درمانی
- ۱. معرفی کوتاه برنامه درمانی و اهداف اصلی آن (با توجه به راهنمای پزشک)
- ۲. مهم‌ترین جنبه‌های این برنامه درمانی بر اساس اطلاعات شخصی بیمار و راهنمای پزشک
- ۳. روش‌های درمان و شیوه‌های مراقبت و مدیریت کلی برنامه درمانی (مطابق با راهنمای پزشک)
- ۴. توضیح نکات اصلی مربوط به سبک زندگی و رژیم غذایی مناسب
- ۵. اگر دارویی تجویز شده، فقط نام داروها و کاربرد اصلی هر کدام را به صورت خلاصه ذکر کن. (از توضیح درباره دوز و توصیه‌های مصرف یا هشدارها خودداری کن.)
- ۶. چه زمانی لازم است به پزشک مراجعه شود یا چه علائمی علامت هشدار هستند
- ۷. پاسخ به سوالات متداول درباره این برنامه درمانی

بخش دوم: مطالب شخصی‌سازی شده برای این بیمار
- لطفاً با توجه به اطلاعات فردی بیمار و راهنمای پزشک، نکات و توصیه‌های اختصاصی متناسب با شرایط او را به صورت کوتاه، کاربردی و عملیاتی بیان کن.
- حتماً راهنمای پزشک را به عنوان مرجع اصلی در نظر بگیر و تمام نکات مهم آن را در پاسخ خود بگنجان.


لطفاً پاسخ را به زبان فارسی و با لحنی دوستانه، علمی و قابل فهم بنویسید. مهم است که تمام اطلاعات ارائه شده با راهنمای پزشک هماهنگ باشد."""

    return prompt


def get_conversation_prompt(condition_data: dict = None) -> ChatPromptTemplate:
    """
    Create conversation prompt template for follow-up questions
    
    Args:
        condition_data: User-specific data about the condition (optional)
    
    Returns:
        ChatPromptTemplate for conversation
    """
    base_system_message = """شما یک دستیار گفتگوی پزشکی هستید که به زبان فارسی با بیماران صحبت می‌کنید.

هدف شما ارائه پاسخ‌های کوتاه، چت‌محور، علمی و قابل فهم به پرسش‌های بیماران درباره برنامه درمانی یا شرایطشان است.
در صورت امکان، پاسخ را مختصر و مفید بیان کنید و به اصل سوال پاسخ دهید.

- لحن دوستانه، صبور و حمایتی
- هشدار درباره موارد جدی که نیاز به مراجعه فوری به پزشک دارند
رعایت نکات زیر ضروری است:
- همیشه به زبان فارسی پاسخ دهید
- اگر سوال خارج از حیطه پزشکی است، محترمانه توضیح دهید که شما فقط می‌توانید درباره موضوعات پزشکی کمک کنید
- اگر سوال نیاز به مشاوره پزشک دارد، حتماً به بیمار توصیه کنید که با پزشک خود مشورت کند
- از طولانی کردن بیش از حد پاسخ بپرهیزید مگر در موارد خاص
- اگر سوال خارج از موضوعات پزشکی بود، محترمانه اعلام کنید که فقط درباره مسائل پزشکی می‌توانید کمک کنید
- اگر سوال به مشاوره پزشک نیاز دارد، بیمار را تشویق کنید با پزشک تماس بگیرد
- از ارائه تجویز دارو یا تشخیص قطعی خودداری کنید
- از ارائه تشخیص قطعی یا تجویز دارو خودداری کنید"""

    # Extract doctor guide and format patient data
    doctor_guide = ""
    data_str = ""
    
    if condition_data:
        doctor_guide = _extract_doctor_guide(condition_data)
        exclude_keys = ["doctor_guide", "doctor_note", "guide", "doctor_instructions", 
                        "medical_guide", "treatment_guide", "plan_guide"]
        data_str = _format_condition_data(condition_data, exclude_keys=exclude_keys)
    
    # Build system message with doctor guide and patient data
    if doctor_guide:
        doctor_guide_section = f"""

راهنمای پزشک برای برنامه درمانی (مرجع اصلی برای تمام پاسخ‌ها):
{doctor_guide}

⚠️ مهم: این راهنمای پزشک باید به عنوان مرجع اصلی در تمام پاسخ‌های شما استفاده شود. تمام توصیه‌ها و اطلاعات باید با این راهنمای پزشک هماهنگ باشد."""
    else:
        doctor_guide_section = ""
    
    if condition_data:
        # Use string concatenation instead of f-string to avoid curly brace conflicts
        system_message = base_system_message + doctor_guide_section + """

اطلاعات شخصی بیمار برای پاسخ‌دهی شخصی‌سازی شده:
""" + (data_str if data_str else "(اطلاعات اضافی موجود نیست)") + """

اطلاعات مورد نیاز در تاریخچه گفتگو نیز موجود است."""
    else:
        system_message = base_system_message + doctor_guide_section + """

اطلاعات مورد نیاز در تاریخچه گفتگو موجود است."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
    
    return prompt


def get_summarization_prompt() -> str:
    """Get prompt for summarizing long conversations"""
    return """لطفاً گفتگوی زیر را به صورت خلاصه و مفید خلاصه کنید، به گونه‌ای که نکات کلیدی و سوالات مهم بیمار حفظ شود:

{conversation}

خلاصه (به زبان فارسی):"""
