"""
Persian prompt templates for medical chatbot
"""
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def _format_condition_data(condition_data: dict) -> str:
    """
    Safely format condition_data to string, handling nested structures
    
    Args:
        condition_data: Dictionary with patient data (may contain nested dicts/lists)
    
    Returns:
        Formatted string representation
    """
    if not condition_data:
        return ""
    
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


def get_educational_prompt(condition_name: str, condition_data: dict) -> str:
    """
    Generate initial educational content prompt in Persian
    
    Args:
        condition_name: Name of the condition in Persian
        condition_data: User-specific data about the condition
    
    Returns:
        Formatted prompt string
    """
    data_str = _format_condition_data(condition_data)
    
    prompt = f"""شما یک دستیار پزشکی هوشمند و آموزشی هستید که به زبان فارسی با بیماران صحبت می‌کنید.

بیمار با بیماری "{condition_name}" مراجعه کرده است.

اطلاعات شخصی بیمار:
{data_str}

لطفا یک یادداشت آموزشی جامع و شخصی‌سازی شده درباره این بیماری بنویسید که با توجه به داده‌های بالینی بیمار باشد.
لطفاً یک متن آموزشی جامع و شخصی‌سازی شده درباره این بیماری برای این بیمار بنویسید که شامل موارد زیر باشد:

بخش اول: اطلاعات کلی و مهم درباره بیماری
- ۱. معرفی کوتاه بیماری و علت‌های اصلی آن
- ۲. مهم‌ترین علائم و نشانه‌های این بیماری بر اساس اطلاعات شخصی بیمار
- ۳. روش‌های درمان رایج و شیوه‌های مراقبت و مدیریت کلی بیماری
- ۴. توضیح نکات اصلی مربوط به سبک زندگی و رژیم غذایی مناسب
- ۵. اگر دارویی تجویز شده، فقط نام داروها و کاربرد اصلی هر کدام را به صورت خلاصه ذکر کن. (از توضیح درباره دوز و توصیه‌های مصرف یا هشدارها خودداری کن.)
- ۶. چه زمانی لازم است به پزشک مراجعه شود یا چه علائمی علامت هشدار هستند
- ۷. پاسخ به سوالات متداول درباره این بیماری

بخش دوم: مطالب شخصی‌سازی شده برای این بیمار
- لطفاً با توجه به اطلاعات فردی بیمار، نکات و توصیه‌های اختصاصی متناسب با شرایط او را به صورت کوتاه، کاربردی و عملیاتی بیان کن.


لطفاً پاسخ را به زبان فارسی و با لحنی دوستانه، علمی و قابل فهم بنویسید."""

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

هدف شما ارائه پاسخ‌های کوتاه، چت‌محور، علمی و قابل فهم به پرسش‌های بیماران درباره بیماری یا شرایطشان است.
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

    # Add patient context if available
    if condition_data:
        data_str = _format_condition_data(condition_data)
        # Use string concatenation instead of f-string to avoid curly brace conflicts
        system_message = base_system_message + """

اطلاعات شخصی بیمار برای پاسخ‌دهی شخصی‌سازی شده:
""" + data_str + """

اطلاعات مورد نیاز در تاریخچه گفتگو نیز موجود است."""
    else:
        system_message = base_system_message + """

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
