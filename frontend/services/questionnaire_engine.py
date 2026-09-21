"""Robust, deterministic, adaptive questionnaire engine for Yojana Sahayak."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class QuestionOption:
    key: str
    label_en: str
    label_hi: str
    description_en: Optional[str] = None
    description_hi: Optional[str] = None
    icon: Optional[str] = None


@dataclass
class Question:
    id: str
    title_en: str
    title_hi: str
    subtitle_en: str
    subtitle_hi: str
    widget_type: str  # "intent_cards", "radio", "select", "number", "text"
    options: List[QuestionOption] = field(default_factory=list)
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    required: bool = True
    placeholder_en: Optional[str] = None
    placeholder_hi: Optional[str] = None
    validation_error_en: Optional[str] = None
    validation_error_hi: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step_value: Optional[float] = None
    default_value: Any = None
    target_field: str = ""  # profile key it maps to


INDIAN_STATES = [
    "All India",
    "Andaman and Nicobar Islands",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chandigarh",
    "Chhattisgarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu and Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Ladakh",
    "Lakshadweep",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Puducherry",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
]

# -------------------------------------------------------------
# Structured Questions Definition (Declarative Rule Graph)
# -------------------------------------------------------------

QUESTIONS: List[Question] = [
    # -------------------------------------------------------------
    # 1. Intent Selection (Always Asked First)
    # -------------------------------------------------------------
    Question(
        id="intent",
        title_en="What are you looking for?",
        title_hi="आप किस प्रकार की योजना या सहायता तलाश रहे हैं?",
        subtitle_en="Select your primary goal to see only relevant questions.",
        subtitle_hi="केवल प्रासंगिक प्रश्न देखने के लिए अपना मुख्य उद्देश्य चुनें।",
        widget_type="intent_cards",
        required=True,
        validation_error_en="Please select an option to continue.",
        validation_error_hi="आगे बढ़ने के लिए कृपया एक विकल्प चुनें।",
        target_field="intent",
        options=[
            QuestionOption("education", "Education & Scholarships", "शिक्षा एवं छात्रवृत्ति", "Tuition aid, scholarships, study support", "छात्रवृत्ति, शिक्षण सहायता", "🎓"),
            QuestionOption("skills", "Internship & Skill Training", "कौशल एवं इंटर्नशिप", "Apprenticeships, free vocational courses & training", "प्रशिक्षुता, तकनीकी प्रशिक्षण", "🛠️"),
            QuestionOption("business", "Business & Loans", "व्यवसाय एवं ऋण", "MSME credit, startup capital, vendor loans", "सूक्ष्म ऋण, व्यवसाय पूंजी", "💼"),
            QuestionOption("agriculture", "Agriculture & Farming", "कृषि एवं किसान कल्याण", "PM-KISAN, crop insurance, equipment", "पीएम-किसान, फसल सहायता", "🌾"),
            QuestionOption("jobs", "Jobs & Employment", "रोजगार एवं आजीविका", "Public work, wage employment, livelihood", "सार्वजनिक कार्य, रोजगार", "🏢"),
            QuestionOption("housing", "Housing & Shelter", "आवास एवं मकान", "PMAY rural & urban housing subsidies", "पक्के मकान हेतु सहायता", "🏠"),
            QuestionOption("healthcare", "Healthcare & Treatment", "स्वास्थ्य एवं चिकित्सा", "Free hospitalization, Ayushman card", "कैशलेस अस्पताल उपचार", "🏥"),
            QuestionOption("pension", "Senior Citizen & Pension", "वरिष्ठ नागरिक एवं पेंशन", "Old age security & monthly pensions", "वृद्धावस्था पेंशन व सुरक्षा", "👴"),
            QuestionOption("women_child", "Women & Child Welfare", "महिला एवं बाल विकास", "Sukanya Samriddhi, maternal assistance", "मातृत्व एवं बालिका योजनाएं", "👩‍👧"),
            QuestionOption("disability", "Disability Support", "दिव्यांगजन सहायता", "Concessional loans, pensions, devices", "सहायक उपकरण व ऋण", "♿"),
            QuestionOption("general", "Explore All Schemes", "सभी योजनाएं देखें", "Check eligibility across all government programs", "सभी सरकारी योजनाओं में जांचें", "🌐"),
        ],
    ),

    # -------------------------------------------------------------
    # 2. Education & Scholarship Flow
    # -------------------------------------------------------------
    Question(
        id="student_type",
        title_en="What is your current level of study?",
        title_hi="आपकी वर्तमान अध्ययन स्थिति क्या है?",
        subtitle_en="Scholarships have distinct eligibility rules for school, college, or research.",
        subtitle_hi="विभिन्न अध्ययन स्तरों के लिए छात्रवृत्ति के अलग नियम हैं।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your current study level to continue.",
        validation_error_hi="आगे बढ़ने के लिए कृपया अपना अध्ययन स्तर चुनें।",
        target_field="dynamic_answers.education_level",
        condition=lambda a: a.get("intent") == "education",
        options=[
            QuestionOption("school", "School Student (Class 1 - 10)", "स्कूली छात्र (कक्षा 1 - 10)"),
            QuestionOption("higher_sec", "Senior Secondary (Class 11 - 12)", "उच्च माध्यमिक (कक्षा 11 - 12)"),
            QuestionOption("college", "College / Undergraduate (Degree)", "कॉलेज / स्नातक (डिग्री)"),
            QuestionOption("postgrad", "Postgraduate / Master's / PhD", "स्नातकोत्तर / शोध (एमए, एमएससी, पीएचडी)"),
            QuestionOption("technical", "ITI / Polytechnic / Vocational Diploma", "आईटीआई / पॉलिटेक्निक / तकनीकी डिप्लोमा"),
        ],
    ),
    Question(
        id="college_course",
        title_en="What course or degree are you pursuing?",
        title_hi="आप कौन सा पाठ्यक्रम या डिग्री कर रहे हैं?",
        subtitle_en="Enables matching with engineering, medical, science, or general scholarships.",
        subtitle_hi="विशिष्ट पाठ्यक्रम छात्रवृत्ति से सटीक मिलान के लिए।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your course or degree to continue.",
        validation_error_hi="आगे बढ़ने के लिए कृपया अपना पाठ्यक्रम चुनें।",
        target_field="dynamic_answers.course",
        condition=lambda a: a.get("intent") == "education" and a.get("student_type") == "college",
        options=[
            QuestionOption("btech", "B.Tech / Engineering / Architecture", "बी.टेक / इंजीनियरिंग / वास्तुकला"),
            QuestionOption("bsc", "B.Sc / Pure Sciences / Agriculture", "बी.एससी / विज्ञान / कृषि"),
            QuestionOption("ba", "B.A / Humanities / Social Sciences", "बी.ए / मानविकी / कला"),
            QuestionOption("bcom", "B.Com / BBA / Management", "बी.कॉम / बीबीए / प्रबंधन"),
            QuestionOption("medical", "MBBS / BDS / Pharmacy / Nursing", "एमबीबीएस / फार्मेसी / नर्सिंग"),
            QuestionOption("other_degree", "Other Undergraduate Degree", "अन्य स्नातक डिग्री"),
        ],
    ),
    Question(
        id="current_year",
        title_en="Which academic year are you currently in?",
        title_hi="आप वर्तमान में किस शैक्षणिक वर्ष में हैं?",
        subtitle_en="Certain scholarships are reserved for first-year entry or continuing renewal.",
        subtitle_hi="कुछ छात्रवृत्तियां प्रथम वर्ष प्रवेश या नवीनीकरण के लिए होती हैं।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your current academic year.",
        validation_error_hi="कृपया अपना वर्तमान शैक्षणिक वर्ष चुनें।",
        target_field="dynamic_answers.current_year",
        condition=lambda a: a.get("intent") == "education" and a.get("student_type") in ("college", "postgrad", "technical"),
        options=[
            QuestionOption("1st_year", "1st Year (Fresh Admission)", "प्रथम वर्ष (नया प्रवेश)"),
            QuestionOption("2nd_year", "2nd Year", "द्वितीय वर्ष"),
            QuestionOption("3rd_year", "3rd Year", "तृतीय वर्ष"),
            QuestionOption("final_year", "4th Year / Final Year", "अंतिम वर्ष"),
        ],
    ),

    # -------------------------------------------------------------
    # 3. Internship & Skill Training Flow
    # -------------------------------------------------------------
    Question(
        id="skill_status",
        title_en="What is your current background?",
        title_hi="आपकी वर्तमान पृष्ठभूमि क्या है?",
        subtitle_en="Helps identify matching national apprenticeship or skill council courses.",
        subtitle_hi="राष्ट्रीय शिक्षुता या कौशल विकास योजनाओं से मिलान में सहायक।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your background to continue.",
        validation_error_hi="कृपया अपनी पृष्ठभूमि चुनें।",
        target_field="dynamic_answers.skill_status",
        condition=lambda a: a.get("intent") == "skills",
        options=[
            QuestionOption("student", "Enrolled College / Technical Student", "कॉलेज अथवा तकनीकी छात्र"),
            QuestionOption("jobseeker", "Job Seeker / Youth seeking practical training", "प्रशिक्षण की तलाश में युवा"),
            QuestionOption("artisan", "Traditional Artisan / Craftsman (Vishwakarma)", "पारंपरिक कारीगर / शिल्पकार"),
        ],
    ),
    Question(
        id="skill_sector",
        title_en="Which sector are you interested in?",
        title_hi="आप किस क्षेत्र में प्रशिक्षण या इंटर्नशिप चाहते हैं?",
        subtitle_en="Skill missions offer domain-specific training subsidies.",
        subtitle_hi="विभिन्न क्षेत्रों में सरकार द्वारा प्रायोजित प्रशिक्षण उपलब्ध हैं।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select a sector of interest.",
        validation_error_hi="कृपया अपनी रुचि का क्षेत्र चुनें।",
        target_field="dynamic_answers.skill_sector",
        condition=lambda a: a.get("intent") == "skills",
        options=[
            QuestionOption("it_digital", "IT & Digital Technologies", "आईटी एवं डिजिटल तकनीक"),
            QuestionOption("manufacturing", "Automotive, Electrical & Manufacturing", "ऑटोमोटिव, इलेक्ट्रिकल एवं विनिर्माण"),
            QuestionOption("healthcare", "Healthcare, Nursing & Hospital Support", "स्वास्थ्य सेवा, नर्सिंग एवं अस्पताल"),
            QuestionOption("handicrafts", "Handicrafts, Textiles & Traditional Arts", "हस्तशिल्प, वस्त्र एवं पारंपरिक कला"),
            QuestionOption("services", "Hospitality, Logistics & Retail", "आतिथ्य, लॉजिस्टिक्स एवं खुदरा"),
        ],
    ),

    # -------------------------------------------------------------
    # 4. Business & Entrepreneurship Flow
    # -------------------------------------------------------------
    Question(
        id="business_stage",
        title_en="What best describes your business stage?",
        title_hi="आपके व्यवसाय का स्वरूप क्या है?",
        subtitle_en="Government credit support varies between street vendors, new startups, and MSMEs.",
        subtitle_hi="सरकारी ऋण सहायता वेंडर, नए व्यवसाय और लघु उद्यम के अनुसार अलग है।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your business stage to continue.",
        validation_error_hi="आगे बढ़ने के लिए कृपया अपने व्यवसाय का चरण चुनें।",
        target_field="dynamic_answers.business_stage",
        condition=lambda a: a.get("intent") == "business",
        options=[
            QuestionOption("existing", "Existing Small Business / Micro Enterprise / Shop", "मौजूदा छोटी दुकान / लघु उद्यम"),
            QuestionOption("street_vendor", "Street Vendor / Artisan / Hawker", "रेहड़ी-पटरी / फेरीवाला / कारीगर"),
            QuestionOption("new_startup", "Planning to Start a New Business", "नया व्यवसाय शुरू करने की योजना"),
        ],
    ),
    Question(
        id="business_sector",
        title_en="What sector does your business operate in?",
        title_hi="आपका व्यवसाय किस क्षेत्र से संबंधित है?",
        subtitle_en="Select the primary industry sector.",
        subtitle_hi="अपने व्यवसाय का मुख्य उद्योग चुनें।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your business sector.",
        validation_error_hi="कृपया अपने व्यवसाय का क्षेत्र चुनें।",
        target_field="dynamic_answers.business_sector",
        condition=lambda a: a.get("intent") == "business",
        options=[
            QuestionOption("retail_trade", "Retail Shop / Trading / Wholesale", "खुदरा दुकान / व्यापार / थोक"),
            QuestionOption("manufacturing", "Manufacturing / Production / Food Processing", "विनिर्माण / उत्पादन / खाद्य प्रसंस्करण"),
            QuestionOption("services", "Services (Repairs, Salon, Transport, IT)", "सेवाएं (मरम्मत, सैलून, परिवहन, आदि)"),
            QuestionOption("artisan_vending", "Street Vending / Traditional Craft", "फेरी / रेहड़ी / पारंपरिक कारीगरी"),
        ],
    ),
    Question(
        id="annual_turnover",
        title_en="What is your business's annual turnover?",
        title_hi="आपके व्यवसाय का वार्षिक टर्नओवर कितना है?",
        subtitle_en="MSME classification and loan limits depend on annual turnover.",
        subtitle_hi="एमएसएमई वर्गीकरण और ऋण सीमा टर्नओवर पर निर्भर करती है।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your annual turnover range.",
        validation_error_hi="कृपया अपना वार्षिक टर्नओवर चुनें।",
        target_field="dynamic_answers.annual_turnover",
        condition=lambda a: a.get("intent") == "business" and a.get("business_stage") == "existing",
        options=[
            QuestionOption("under_5lakh", "Under ₹5 Lakhs", "₹5 लाख से कम"),
            QuestionOption("5_to_25lakh", "₹5 Lakhs – ₹25 Lakhs", "₹5 लाख – ₹25 लाख"),
            QuestionOption("25lakh_to_1cr", "₹25 Lakhs – ₹1 Crore", "₹25 लाख – ₹1 करोड़"),
            QuestionOption("above_1cr", "Above ₹1 Crore", "₹1 करोड़ से अधिक"),
        ],
    ),
    Question(
        id="employees_count",
        title_en="How many people do you employ?",
        title_hi="आपके व्यवसाय में कितने कर्मचारी कार्य करते हैं?",
        subtitle_en="Staff count determines micro vs small enterprise aid.",
        subtitle_hi="कर्मचारियों की संख्या सूक्ष्म अथवा लघु उद्यम सहायता तय करती है।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select the employee count range.",
        validation_error_hi="कृपया कर्मचारियों की संख्या चुनें।",
        target_field="dynamic_answers.employees_count",
        condition=lambda a: a.get("intent") == "business" and a.get("business_stage") == "existing",
        options=[
            QuestionOption("1_to_5", "1 to 5 employees (Micro)", "1 से 5 कर्मचारी (सूक्ष्म)"),
            QuestionOption("6_to_20", "6 to 20 employees (Small)", "6 से 20 कर्मचारी (लघु)"),
            QuestionOption("above_20", "More than 20 employees", "20 से अधिक कर्मचारी"),
        ],
    ),
    Question(
        id="funding_need",
        title_en="What type of funding are you seeking?",
        title_hi="आपको किस प्रकार के वित्तीय सहयोग की आवश्यकता है?",
        subtitle_en="Connects with MUDRA (Shishu, Kishore, Tarun) or PM-SVANidhi loans.",
        subtitle_hi="मुद्रा या पीएम-स्वनिधि ऋण से जोड़ने के लिए।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your funding requirement.",
        validation_error_hi="कृपया अपनी वित्तीय आवश्यकता चुनें।",
        target_field="dynamic_answers.funding_need",
        condition=lambda a: a.get("intent") == "business",
        options=[
            QuestionOption("micro_loan", "Micro Working Capital (Up to ₹50,000 / PM-SVANidhi)", "कार्यशील पूंजी (₹50,000 तक)"),
            QuestionOption("mudra_loan", "MUDRA Loan (₹50,000 to ₹10 Lakhs)", "मुद्रा ऋण (₹50,000 से ₹10 लाख)"),
            QuestionOption("startup_grant", "Startup Grant / Subsidized Equipment Credit", "स्टार्टअप अनुदान / उपकरण ऋण"),
        ],
    ),

    # -------------------------------------------------------------
    # 5. Agriculture & Farming Flow
    # -------------------------------------------------------------
    Question(
        id="farmer_type",
        title_en="What is your agricultural role?",
        title_hi="कृषि में आपकी मुख्य भूमिका क्या है?",
        subtitle_en="Direct benefit transfers are linked to land title ownership.",
        subtitle_hi="प्रत्यक्ष लाभ अंतरण भूमि स्वामित्व से जुड़ा होता है।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your farming status to continue.",
        validation_error_hi="कृपया अपनी कृषि भूमिका चुनें।",
        target_field="dynamic_answers.farmer_type",
        condition=lambda a: a.get("intent") == "agriculture",
        options=[
            QuestionOption("landowner", "Landowning Cultivator Farmer", "भूमिधारक किसान"),
            QuestionOption("tenant", "Tenant Farmer / Sharecropper", "बटाईदार / किरायेदार किसान"),
            QuestionOption("agri_worker", "Agricultural Laborer (Landless)", "भूमिहीन कृषि मजदूर"),
        ],
    ),
    Question(
        id="landholding",
        title_en="What is your agricultural landholding size?",
        title_hi="आपकी कृषि भूमि का आकार कितना है?",
        subtitle_en="PM-KISAN prioritizes small and marginal cultivators.",
        subtitle_hi="पीएम-किसान लघु एवं सीमांत किसानों को प्राथमिकता देती है।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your landholding size to continue.",
        validation_error_hi="कृपया अपनी भूमि का आकार चुनें।",
        target_field="dynamic_answers.landholding",
        condition=lambda a: a.get("intent") == "agriculture" and a.get("farmer_type") == "landowner",
        options=[
            QuestionOption("marginal", "Small & Marginal Farmer (Up to 2 hectares / 5 acres)", "लघु एवं सीमांत किसान (2 हेक्टेयर तक)"),
            QuestionOption("medium_large", "Medium / Large Farmer (More than 2 hectares)", "मध्यम या बड़ा किसान (2 हेक्टेयर से अधिक)"),
        ],
    ),
    Question(
        id="crop_activity",
        title_en="What is your primary crop or farming activity?",
        title_hi="आपकी मुख्य फसल या कृषि गतिविधि क्या है?",
        subtitle_en="Helps identify crop insurance (PMFBY), irrigation, and horticulture aid.",
        subtitle_hi="फसल बीमा (पीएमएफबीवाई) और बागवानी योजनाओं के लिए।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your farming activity.",
        validation_error_hi="कृपया अपनी कृषि गतिविधि चुनें।",
        target_field="dynamic_answers.crop_activity",
        condition=lambda a: a.get("intent") == "agriculture",
        options=[
            QuestionOption("grains", "Food Grains (Paddy, Wheat, Pulses, Millets)", "अन्न एवं दालें (धान, गेहूं, बाजरा)"),
            QuestionOption("cash_crops", "Cash Crops (Sugarcane, Cotton, Oilseeds)", "व्यावसायिक फसलें (गन्ना, कपास, तिलहन)"),
            QuestionOption("horticulture", "Horticulture, Vegetables & Fruits", "बागवानी, फल एवं सब्जियां"),
            QuestionOption("dairy_allied", "Dairy, Poultry, Fisheries & Animal Husbandry", "डेयरी, पशुपालन एवं मत्स्य पालन"),
        ],
    ),

    # -------------------------------------------------------------
    # 6. Jobs & Employment Flow
    # -------------------------------------------------------------
    Question(
        id="employment_status",
        title_en="What is your current employment status?",
        title_hi="आपकी वर्तमान रोजगार स्थिति क्या है?",
        subtitle_en="Identifies eligibility for MGNREGA or employment exchange initiatives.",
        subtitle_hi="मनरेगा अथवा रोजगार सहायता योजनाओं से मिलान में सहायक।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your employment status.",
        validation_error_hi="कृपया अपनी रोजगार स्थिति चुनें।",
        target_field="dynamic_answers.employment_status",
        condition=lambda a: a.get("intent") == "jobs",
        options=[
            QuestionOption("unemployed", "Actively looking for work", "सक्रिय रूप से काम की तलाश में"),
            QuestionOption("daily_wage", "Daily wage / Informal manual worker", "दैनिक वेतनभोगी / अनौपचारिक श्रमिक"),
            QuestionOption("recent_grad", "Recent graduate seeking first employment", "पहली नौकरी की तलाश में युवा"),
        ],
    ),
    Question(
        id="qualification",
        title_en="What is your highest educational qualification?",
        title_hi="आपकी उच्चतम शैक्षणिक योग्यता क्या है?",
        subtitle_en="Public employment and training schemes set minimum educational standards.",
        subtitle_hi="सार्वजनिक रोजगार और प्रशिक्षण हेतु आवश्यक।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your educational qualification.",
        validation_error_hi="कृपया अपनी शैक्षणिक योग्यता चुनें।",
        target_field="dynamic_answers.qualification",
        condition=lambda a: a.get("intent") == "jobs",
        options=[
            QuestionOption("below_10th", "Below 10th Standard", "10वीं से कम"),
            QuestionOption("10th_pass", "10th Pass (Matriculation)", "10वीं पास"),
            QuestionOption("12th_pass", "12th Pass (Higher Secondary)", "12वीं पास"),
            QuestionOption("graduate", "Graduate / Bachelor's Degree", "स्नातक डिग्री"),
            QuestionOption("iti_diploma", "ITI / Polytechnic Diploma", "आईटीआई / डिप्लोमा"),
        ],
    ),

    # -------------------------------------------------------------
    # 7. Common Demographic Questions (Only When Relevant)
    # -------------------------------------------------------------
    Question(
        id="age",
        title_en="What is your age in completed years?",
        title_hi="आपकी आयु कितने वर्ष है?",
        subtitle_en="Many youth, pension, and employment schemes enforce age limits.",
        subtitle_hi="आयु सीमा के आधार पर पात्रता निर्धारित करने के लिए।",
        widget_type="number",
        required=True,
        min_value=1.0,
        max_value=120.0,
        step_value=1.0,
        default_value=25.0,
        placeholder_en="Enter your age (e.g. 25)",
        placeholder_hi="अपनी आयु दर्ज करें (उदा. 25)",
        validation_error_en="Please enter a valid age between 1 and 120 years.",
        validation_error_hi="कृपया 1 से 120 वर्ष के बीच एक मान्य आयु दर्ज करें।",
        target_field="age",
        # Ask age for pension, women_child, jobs, or general
        condition=lambda a: a.get("intent") in ("pension", "women_child", "jobs", "general"),
    ),
    Question(
        id="social_category",
        title_en="What is your social category?",
        title_hi="आपकी सामाजिक श्रेणी क्या है?",
        subtitle_en="Targeted affirmative action programs and scholarships reserve quota by category.",
        subtitle_hi="आरक्षण एवं लक्षित कल्याणकारी योजनाओं के सत्यापन हेतु।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your social category to continue.",
        validation_error_hi="कृपया अपनी सामाजिक श्रेणी चुनें।",
        target_field="category",
        # Ask for education, business, housing, jobs, skills, general; skip for pure agriculture where PM-KISAN is universal
        condition=lambda a: a.get("intent") in ("education", "business", "housing", "jobs", "skills", "general"),
        options=[
            QuestionOption("General", "General", "सामान्य"),
            QuestionOption("OBC", "OBC (Other Backward Class)", "ओबीसी"),
            QuestionOption("SC", "SC (Scheduled Caste)", "अनुसूचित जाति (एससी)"),
            QuestionOption("ST", "ST (Scheduled Tribe)", "अनुसूचित जनजाति (एसटी)"),
            QuestionOption("EWS", "EWS (Economically Weaker Section)", "ईडब्ल्यूएस"),
        ],
    ),
    Question(
        id="annual_income",
        title_en="What is your approximate annual family income?",
        title_hi="आपके परिवार की कुल वार्षिक आय कितनी है?",
        subtitle_en="Government welfare assistance prioritizes households below specific income caps.",
        subtitle_hi="सरकारी सहायता आय सीमा के आधार पर दी जाती है।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select your annual income range.",
        validation_error_hi="कृपया अपनी वार्षिक आय श्रेणी चुनें।",
        target_field="annual_income",
        # Ask for education, business, housing, healthcare, pension, general
        condition=lambda a: a.get("intent") in ("education", "business", "housing", "healthcare", "pension", "general"),
        options=[
            QuestionOption("100000", "Under ₹1.5 Lakh", "₹1.5 लाख से कम"),
            QuestionOption("250000", "₹1.5 Lakh – ₹3 Lakh", "₹1.5 लाख – ₹3 लाख"),
            QuestionOption("500000", "₹3 Lakh – ₹8 Lakh", "₹3 लाख – ₹8 लाख"),
            QuestionOption("900000", "Above ₹8 Lakh", "₹8 लाख से अधिक"),
            QuestionOption("unknown", "Not sure / Prefer not to specify", "निश्चित नहीं"),
        ],
    ),
    Question(
        id="area",
        title_en="Where is your residence located?",
        title_hi="आप कहाँ रहते हैं?",
        subtitle_en="Schemes like PMAY and rural development initiatives require area distinction.",
        subtitle_hi="आवास एवं ग्रामीण विकास योजनाओं के लिए आवश्यक।",
        widget_type="radio",
        required=True,
        validation_error_en="Please select where you live.",
        validation_error_hi="कृपया अपने निवास का क्षेत्र चुनें।",
        target_field="area",
        # Ask for housing, agriculture, general, jobs
        condition=lambda a: a.get("intent") in ("housing", "agriculture", "general", "jobs"),
        options=[
            QuestionOption("Rural", "Rural (Village / Gram Panchayat)", "ग्रामीण (गांव / ग्राम पंचायत)"),
            QuestionOption("Urban", "Urban (City / Municipality)", "शहरी (शहर / नगर पालिका)"),
        ],
    ),
    Question(
        id="state",
        title_en="Select your State or Union Territory",
        title_hi="अपना राज्य या केंद्र शासित प्रदेश चुनें",
        subtitle_en="To discover both Central and State Government welfare schemes.",
        subtitle_hi="केंद्रीय एवं राज्य स्तरीय योजनाओं से सटीक मिलान के लिए।",
        widget_type="select",
        required=True,
        placeholder_en="Select your state...",
        placeholder_hi="अपना राज्य चुनें...",
        validation_error_en="Please select your state to continue.",
        validation_error_hi="आगे बढ़ने के लिए कृपया अपना राज्य चुनें।",
        target_field="state",
        options=[QuestionOption(s, s, s) for s in INDIAN_STATES],
    ),
]


class QuestionnaireEngine:
    """Manages dynamic progression, validation, and canonical state synchronization."""

    def __init__(self, questions: Optional[List[Question]] = None):
        self.questions = questions or QUESTIONS

    def get_active_questions(self, answers: Dict[str, Any]) -> List[Question]:
        """Resolves only questions whose condition passes given current answers."""
        active = []
        for q in self.questions:
            if q.condition is None or q.condition(answers):
                active.append(q)
        return active

    def validate_answer(self, question: Question, value: Any, lang: str = "en") -> Tuple[bool, Optional[str]]:
        """Validates answer against question definition and domain rules."""
        err_msg = question.validation_error_hi if lang == "hi" else question.validation_error_en
        if not err_msg:
            err_msg = "Please answer this required question to continue." if lang != "hi" else "कृपया आगे बढ़ने के लिए इस प्रश्न का उत्तर दें।"

        # If not required and value is missing, pass
        if not question.required and (value is None or value == ""):
            return True, None

        # Check missing or empty
        if value is None or value == "":
            return False, err_msg

        # Check placeholder strings (never treat placeholder as valid answer)
        placeholder = question.placeholder_hi if lang == "hi" else question.placeholder_en
        if placeholder and value == placeholder:
            return False, err_msg
        if isinstance(value, str) and value.lower() in ("select", "select state", "choose option", "none"):
            return False, err_msg

        # Type-specific validation
        if question.widget_type == "select":
            # Value must be one of the option keys
            valid_keys = [o.key for o in question.options]
            if value not in valid_keys:
                return False, err_msg

        elif question.widget_type == "radio":
            valid_keys = [o.key for o in question.options]
            if value not in valid_keys:
                return False, err_msg

        elif question.widget_type == "number":
            try:
                num = float(value)
                if question.min_value is not None and num < question.min_value:
                    return False, err_msg
                if question.max_value is not None and num > question.max_value:
                    return False, err_msg
            except (ValueError, TypeError):
                return False, err_msg

        return True, None

    def clean_stale_answers(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Removes answers to questions that are no longer active due to conditional changes."""
        active_ids = {q.id for q in self.get_active_questions(answers)}
        # Retain intent always
        active_ids.add("intent")
        cleaned = {}
        for k, v in answers.items():
            if k in active_ids:
                cleaned[k] = v
        return cleaned

    def build_profile_payload(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Transforms cleaned active answers into normalized CitizenProfileInput dictionary."""
        cleaned_answers = self.clean_stale_answers(answers)
        intent = cleaned_answers.get("intent", "general")
        state = cleaned_answers.get("state")
        if state == "ALL" or not state:
            state = None

        # Parse income
        income_raw = cleaned_answers.get("annual_income")
        annual_income = None
        if income_raw and income_raw != "unknown":
            try:
                annual_income = float(income_raw)
            except ValueError:
                annual_income = None

        # Determine occupation from intent or sub-questions
        occupation = None
        if intent == "agriculture":
            occupation = "farmer"
        elif intent == "education":
            occupation = "student"
        elif intent == "business":
            occupation = "self-employed"
            if cleaned_answers.get("business_stage") == "street_vendor":
                occupation = "street vendor"
        elif intent == "jobs":
            occupation = "unemployed"
        elif intent == "pension":
            occupation = "retired"

        category = cleaned_answers.get("social_category")
        area = cleaned_answers.get("area")
        disability = (intent == "disability") or bool(cleaned_answers.get("disability", False))

        # Dynamic answer bundle
        dynamic_answers = {
            "education_level": cleaned_answers.get("student_type"),
            "course": cleaned_answers.get("college_course"),
            "current_year": cleaned_answers.get("current_year"),
            "skill_status": cleaned_answers.get("skill_status"),
            "skill_sector": cleaned_answers.get("skill_sector"),
            "business_stage": cleaned_answers.get("business_stage"),
            "business_sector": cleaned_answers.get("business_sector"),
            "annual_turnover": cleaned_answers.get("annual_turnover"),
            "employees_count": cleaned_answers.get("employees_count"),
            "funding_need": cleaned_answers.get("funding_need"),
            "farmer_type": cleaned_answers.get("farmer_type"),
            "landholding": cleaned_answers.get("landholding"),
            "crop_activity": cleaned_answers.get("crop_activity"),
            "employment_status": cleaned_answers.get("employment_status"),
            "qualification": cleaned_answers.get("qualification"),
        }
        # Filter None
        dynamic_answers = {k: v for k, v in dynamic_answers.items() if v is not None}

        # Need mapping
        needs = []
        if intent == "education":
            needs = ["Education & scholarships"]
        elif intent == "business":
            needs = ["Business & loans"]
        elif intent == "agriculture":
            needs = ["Agriculture"]
        elif intent in ("jobs", "skills"):
            needs = ["Employment & skills"]
        elif intent == "housing":
            needs = ["Housing"]
        elif intent == "healthcare":
            needs = ["Health"]
        elif intent == "pension":
            needs = ["Pension"]
        elif intent == "women_child":
            needs = ["Women & child"]
        elif intent == "disability":
            needs = ["Disability support"]

        return {
            "state": state,
            "age": int(cleaned_answers["age"]) if "age" in cleaned_answers and cleaned_answers["age"] is not None else None,
            "annual_income": annual_income,
            "occupation": occupation,
            "category": category,
            "area": area,
            "disability": disability,
            "intent": intent,
            "needs": needs,
            "dynamic_answers": dynamic_answers,
            "requirement": ", ".join(needs) if needs else None,
        }


questionnaire_engine = QuestionnaireEngine()
