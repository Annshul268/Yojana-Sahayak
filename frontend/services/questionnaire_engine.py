"""Robust, sector-aware, grouped questionnaire engine for Yojana Sahayak."""

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
class QuestionField:
    id: str
    label_en: str
    label_hi: str
    help_en: Optional[str] = None
    help_hi: Optional[str] = None
    widget_type: str = "select"  # "select", "radio", "number", "text", "intent_cards"
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
    target_field: str = ""


@dataclass
class QuestionGroup:
    id: str
    title_en: str
    title_hi: str
    subtitle_en: str
    subtitle_hi: str
    fields: List[QuestionField]
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None


# Comprehensive Indian States and Union Territories list
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

# Backward-compatibility alias
OCCUPATION_OPTIONS = [
    ("student", "🎓 Student", "विद्यार्थी"),
    ("farmer", "🌾 Farmer / Agri", "किसान"),
    ("self-employed", "💼 Self-Employed / Business", "स्वरोजगार"),
    ("salaried", "🏢 Salaried Employee", "नौकरीपेशा"),
    ("street vendor", "🛒 Street Vendor / Artisan", "रेहड़ी-पटरी / कारीगर"),
    ("unemployed", "🔍 Looking for Work", "बेरोजगार"),
    ("retired", "👴 Senior / Retired", "वरिष्ठ नागरिक"),
    ("other", "✨ Other", "अन्य"),
]


# -------------------------------------------------------------
# 1. Intent / Goal Question Group (Always Step 0)
# -------------------------------------------------------------
INTENT_GROUP = QuestionGroup(
    id="intent_selection",
    title_en="What are you looking for?",
    title_hi="आप किस प्रकार की योजना या सहायता तलाश रहे हैं?",
    subtitle_en="Select your primary goal to see only relevant questions — no unnecessary forms.",
    subtitle_hi="केवल प्रासंगिक प्रश्न देखने के लिए अपना मुख्य उद्देश्य चुनें।",
    fields=[
        QuestionField(
            id="intent",
            label_en="Primary Goal",
            label_hi="मुख्य उद्देश्य",
            widget_type="intent_cards",
            required=True,
            validation_error_en="Please select a primary goal to continue.",
            validation_error_hi="आगे बढ़ने के लिए कृपया एक उद्देश्य चुनें।",
            options=[
                QuestionOption("education", "Education & Scholarships", "शिक्षा एवं छात्रवृत्ति", "Tuition aid, scholarships, study support", "छात्रवृत्ति, शिक्षण सहायता", "🎓"),
                QuestionOption("internships", "Internships / Apprenticeships", "इंटर्नशिप एवं शिक्षुता", "PM Internship Scheme, industrial stipends", "पीएम इंटर्नशिप, शिक्षुता वजीफा", "💼"),
                QuestionOption("jobs", "Jobs & Employment", "रोजगार एवं आजीविका", "Public work, wage employment, recruitment", "सार्वजनिक कार्य, रोजगार", "🏢"),
                QuestionOption("skills", "Skill Development / Training", "कौशल विकास एवं प्रशिक्षण", "PMKVY, free technical & vocational courses", "नि:शुल्क व्यावसायिक प्रशिक्षण", "🛠️"),
                QuestionOption("business", "Business & Entrepreneurship", "व्यवसाय एवं ऋण", "PMMY micro-loans, MSME credit, vendor loans", "सूक्ष्म ऋण, व्यवसाय पूंजी", "📈"),
                QuestionOption("agriculture", "Agriculture & Farming", "कृषि एवं किसान कल्याण", "PM-KISAN income, crop insurance, equipment", "पीएम-किसान, फसल सहायता", "🌾"),
                QuestionOption("housing", "Housing & Shelter", "आवास एवं मकान", "PMAY rural & urban pucca house grants", "पक्के मकान हेतु सहायता", "🏠"),
                QuestionOption("healthcare", "Healthcare & Treatment", "स्वास्थ्य एवं चिकित्सा", "Free hospitalization, Ayushman card", "कैशलेस अस्पताल उपचार", "🏥"),
                QuestionOption("financial", "Financial Assistance", "वित्तीय सहायता", "Direct benefit transfers and emergency relief", "प्रत्यक्ष लाभ हस्तांतरण (DBT)", "💳"),
                QuestionOption("women_child", "Women & Child Welfare", "महिला एवं बाल विकास", "Sukanya Samriddhi, maternal assistance", "मातृत्व एवं बालिका योजनाएं", "👩‍👧"),
                QuestionOption("pension", "Senior Citizens & Pension", "वरिष्ठ नागरिक एवं पेंशन", "Old age security & monthly pensions", "वृद्धावस्था पेंशन व सुरक्षा", "👴"),
                QuestionOption("disability", "Disability Support (Divyangjan)", "दिव्यांगजन सहायता", "Concessional loans, devices, pensions", "सहायक उपकरण व ऋण", "♿"),
                QuestionOption("social_welfare", "Social Welfare", "समाज कल्याण", "SC/ST/EWS marginalized community support", "हाशिए के वर्गों हेतु सहायता", "🤝"),
                QuestionOption("general", "Explore All Benefits", "सभी योजनाएं देखें", "Check eligibility across all government programs", "सभी सरकारी योजनाओं में जांचें", "🌐"),
            ],
        )
    ],
)


# -------------------------------------------------------------
# 2. Location & Personal Details Group (Common Step 1)
# -------------------------------------------------------------
LOCATION_PERSONAL_GROUP = QuestionGroup(
    id="location_personal",
    title_en="Location & Basic Details",
    title_hi="स्थान एवं बुनियादी विवरण",
    subtitle_en="Welfare schemes vary between Central Government and individual State Governments.",
    subtitle_hi="केंद्रीय एवं राज्य स्तरीय योजनाओं से सटीक मिलान हेतु अपना विवरण दें।",
    fields=[
        QuestionField(
            id="state",
            label_en="State / Union Territory",
            label_hi="राज्य / केंद्र शासित प्रदेश",
            help_en="Select your home state or state of domicile.",
            help_hi="अपना गृह राज्य या अधिवास राज्य चुनें।",
            widget_type="select",
            required=True,
            placeholder_en="Select your state...",
            placeholder_hi="अपना राज्य चुनें...",
            validation_error_en="Please select your state to continue.",
            validation_error_hi="आगे बढ़ने के लिए कृपया अपना राज्य चुनें।",
            options=[QuestionOption(s, s, s) for s in INDIAN_STATES],
        ),
        QuestionField(
            id="district",
            label_en="District (Optional)",
            label_hi="जिला (वैकल्पिक)",
            help_en="Helps identify district-level welfare programs.",
            help_hi="जिला स्तरीय कल्याणकारी योजनाओं की पहचान में सहायक।",
            widget_type="text",
            required=False,
            placeholder_en="Enter your district (e.g. Gorakhpur, Pune)...",
            placeholder_hi="अपना जिला दर्ज करें...",
        ),
        QuestionField(
            id="area",
            label_en="Residence Area",
            label_hi="निवास क्षेत्र",
            help_en="Schemes often have specific components for rural or urban citizens.",
            help_hi="ग्रामीण और शहरी नागरिकों हेतु योजनाओं में अलग प्रावधान होते हैं।",
            widget_type="radio",
            required=True,
            validation_error_en="Please select your residence area.",
            validation_error_hi="कृपया अपना निवास क्षेत्र चुनें।",
            options=[
                QuestionOption("Rural", "Rural (Village / Gram Panchayat)", "ग्रामीण (गांव / ग्राम पंचायत)"),
                QuestionOption("Urban", "Urban (City / Municipality)", "शहरी (शहर / नगर पालिका)"),
            ],
        ),
        QuestionField(
            id="age",
            label_en="Age (in completed years)",
            label_hi="आयु (पूर्ण वर्षों में)",
            help_en="Enter your exact age. Schemes use specific age brackets.",
            help_hi="अपनी वास्तविक आयु दर्ज करें।",
            widget_type="number",
            required=True,
            min_value=0.0,
            max_value=120.0,
            step_value=1.0,
            placeholder_en="e.g. 21",
            placeholder_hi="उदा. 21",
            validation_error_en="Please enter a valid age between 0 and 120.",
            validation_error_hi="कृपया 0 से 120 के बीच मान्य आयु दर्ज करें।",
        ),
        QuestionField(
            id="gender",
            label_en="Gender",
            label_hi="लिंग",
            help_en="Many schemes specifically empower women or special categories.",
            help_hi="विशिष्ट योजनाएं बालिकाओं और महिलाओं को सशक्त बनाती हैं।",
            widget_type="radio",
            required=True,
            validation_error_en="Please select your gender.",
            validation_error_hi="कृपया अपना लिंग चुनें।",
            options=[
                QuestionOption("female", "Female", "महिला"),
                QuestionOption("male", "Male", "पुरुष"),
                QuestionOption("other", "Other / Transgender", "अन्य / ट्रांसजेंडर"),
                QuestionOption("prefer_not_to_say", "Prefer not to say", "बताना नहीं चाहते"),
            ],
        ),
        QuestionField(
            id="marital_status",
            label_en="Marital Status (Optional)",
            label_hi="वैवाहिक स्थिति (वैकल्पिक)",
            widget_type="select",
            required=False,
            placeholder_en="Select marital status...",
            placeholder_hi="वैवाहिक स्थिति चुनें...",
            options=[
                QuestionOption("single", "Single / Unmarried", "अविवाहित"),
                QuestionOption("married", "Married", "विवाहित"),
                QuestionOption("widowed", "Widow / Widower", "विधवा / विधुर"),
                QuestionOption("divorced", "Divorced / Separated", "तलाकशुदा / अलग"),
                QuestionOption("prefer_not_to_say", "Prefer not to say", "बताना नहीं चाहते"),
            ],
        ),
    ],
)


# -------------------------------------------------------------
# 3. Economic & Social Profile Group (Common Step 2)
# -------------------------------------------------------------
ECONOMIC_SOCIAL_GROUP = QuestionGroup(
    id="economic_social",
    title_en="Economic & Social Background",
    title_hi="आर्थिक एवं सामाजिक पृष्ठभूमि",
    subtitle_en="Government welfare schemes use official income ceilings and reservation criteria.",
    subtitle_hi="सरकारी योजनाएं आधिकारिक आय सीमा और सामाजिक श्रेणियों के अनुसार लाभ देती हैं।",
    fields=[
        QuestionField(
            id="annual_income",
            label_en="Approximate Annual Family Income (₹ in INR)",
            label_hi="अनुमानित वार्षिक पारिवारिक आय (₹ रुपये में)",
            help_en="Total combined household earnings from all sources in rupees per year (e.g. 150000).",
            help_hi="सभी स्रोतों से कुल वार्षिक पारिवारिक आय (उदा. 150000)।",
            widget_type="number",
            required=True,
            min_value=0.0,
            max_value=10000000.0,
            step_value=10000.0,
            placeholder_en="Enter amount in ₹ (e.g. 200000)",
            placeholder_hi="रुपये में राशि दर्ज करें (उदा. 200000)",
            validation_error_en="Please enter a valid family income (₹ 0 or greater).",
            validation_error_hi="कृपया मान्य पारिवारिक आय (₹ 0 या अधिक) दर्ज करें।",
        ),
        QuestionField(
            id="social_category",
            label_en="Social Category",
            label_hi="सामाजिक श्रेणी",
            help_en="Specific reservations and grants are notified for designated categories.",
            help_hi="आरक्षण और विशेष अनुदान अधिसूचित श्रेणियों के लिए लागू होते हैं।",
            widget_type="radio",
            required=True,
            validation_error_en="Please select your social category.",
            validation_error_hi="कृपया अपनी सामाजिक श्रेणी चुनें।",
            options=[
                QuestionOption("General", "General (Unreserved)", "सामान्य (अनारक्षित)"),
                QuestionOption("OBC", "OBC (Other Backward Classes)", "अन्य पिछड़ा वर्ग (OBC)"),
                QuestionOption("SC", "SC (Scheduled Caste)", "अनुसूचित जाति (SC)"),
                QuestionOption("ST", "ST (Scheduled Tribe)", "अनुसूचित जनजाति (ST)"),
                QuestionOption("EWS", "EWS (Economically Weaker Section)", "आर्थिक रूप से कमजोर वर्ग (EWS)"),
            ],
        ),
        QuestionField(
            id="disability",
            label_en="Person with Benchmark Disability (Divyangjan)?",
            label_hi="क्या आप दिव्यांगजन (विशिष्ट आवश्यकता वाले व्यक्ति) हैं?",
            help_en="Select Yes if holding a Disability Certificate / UDID card (40% or more).",
            help_hi="दिव्यांगता प्रमाणपत्र / UDID धारक होने पर 'हाँ' चुनें।",
            widget_type="radio",
            required=True,
            validation_error_en="Please indicate your disability status.",
            validation_error_hi="कृपया दिव्यांगता स्थिति इंगित करें।",
            options=[
                QuestionOption("no", "No", "नहीं"),
                QuestionOption("yes", "Yes (40% or more benchmark disability)", "हाँ (40% या अधिक दिव्यांगता)"),
                QuestionOption("prefer_not_to_say", "Prefer not to say", "बताना नहीं चाहते"),
            ],
        ),
        QuestionField(
            id="minority_status",
            label_en="Belong to a Notified Religious Minority Community?",
            label_hi="क्या आप अधिसूचित अल्पसंख्यक समुदाय से हैं?",
            help_en="Muslim, Christian, Sikh, Buddhist, Jain, or Parsi communities.",
            help_hi="मुस्लिम, ईसाई, सिख, बौद्ध, जैन, अथवा पारसी समुदाय।",
            widget_type="radio",
            required=True,
            validation_error_en="Please select minority status.",
            validation_error_hi="कृपया अल्पसंख्यक स्थिति चुनें।",
            options=[
                QuestionOption("no", "No", "नहीं"),
                QuestionOption("yes", "Yes", "हाँ"),
                QuestionOption("prefer_not_to_say", "Prefer not to say", "बताना नहीं चाहते"),
            ],
        ),
    ],
)


# -------------------------------------------------------------
# 4. Sector-Specific Question Groups (Adaptive Step 3)
# -------------------------------------------------------------

# Sector: Education & Scholarships
EDUCATION_GROUP = QuestionGroup(
    id="sector_education",
    title_en="Education & Scholarship Details",
    title_hi="शिक्षा एवं छात्रवृत्ति विवरण",
    subtitle_en="Scholarships have distinct criteria based on course level, institution, and study status.",
    subtitle_hi="विभिन्न अध्ययन स्तरों और पाठ्यक्रमों हेतु छात्रवृत्ति के अलग नियम हैं।",
    condition=lambda a: a.get("intent") == "education",
    fields=[
        QuestionField(
            id="education_level",
            label_en="Current Level of Study",
            label_hi="वर्तमान अध्ययन स्तर",
            widget_type="radio",
            required=True,
            validation_error_en="Please select your current study level.",
            validation_error_hi="कृपया अपना अध्ययन स्तर चुनें।",
            options=[
                QuestionOption("school", "School Student (Class 1 - 10)", "स्कूली छात्र (कक्षा 1 - 10)"),
                QuestionOption("higher_sec", "Senior Secondary (Class 11 - 12)", "उच्च माध्यमिक (कक्षा 11 - 12)"),
                QuestionOption("undergraduate", "College / Undergraduate Degree (BA, BSc, BTech, BCom, MBBS)", "कॉलेज / स्नातक डिग्री"),
                QuestionOption("postgraduate", "Postgraduate / Master's / PhD / Research", "स्नातकोत्तर / शोध (एमए, एमएससी, पीएचडी)"),
                QuestionOption("vocational", "ITI / Polytechnic / Vocational Diploma", "आईटीआई / पॉलिटेक्निक / तकनीकी डिप्लोमा"),
            ],
        ),
        QuestionField(
            id="course_name",
            label_en="Course / Degree Name",
            label_hi="पाठ्यक्रम या डिग्री का नाम",
            widget_type="text",
            required=True,
            placeholder_en="e.g. B.Tech Computer Science, Class 12 Science, BA...",
            placeholder_hi="उदा. बी.टेक, 12वीं विज्ञान, बीए...",
            validation_error_en="Please enter your course or degree name.",
            validation_error_hi="कृपया अपने पाठ्यक्रम का नाम दर्ज करें।",
        ),
        QuestionField(
            id="institution_type",
            label_en="Institution Type",
            label_hi="संस्थान का प्रकार",
            widget_type="radio",
            required=True,
            validation_error_en="Please select institution type.",
            validation_error_hi="कृपया संस्थान प्रकार चुनें।",
            options=[
                QuestionOption("government", "Government / Aided School or College", "सरकारी / सहायता प्राप्त संस्थान"),
                QuestionOption("private_recognized", "Private Recognized Institution", "निजी मान्यता प्राप्त संस्थान"),
                QuestionOption("other", "Other", "अन्य"),
            ],
        ),
    ],
)

# Sector: Internships & Apprenticeships
INTERNSHIP_GROUP = QuestionGroup(
    id="sector_internships",
    title_en="Internship & Qualification Details",
    title_hi="इंटर्नशिप एवं योग्यता विवरण",
    subtitle_en="Details required for PM Internship Scheme and corporate apprenticeships.",
    subtitle_hi="पीएम इंटर्नशिप योजना और औद्योगिक शिक्षुता हेतु आवश्यक विवरण।",
    condition=lambda a: a.get("intent") == "internships",
    fields=[
        QuestionField(
            id="highest_qualification",
            label_en="Highest Qualification Completed / Pursuing",
            label_hi="उच्चतम शैक्षणिक योग्यता",
            widget_type="select",
            required=True,
            placeholder_en="Select qualification...",
            placeholder_hi="योग्यता चुनें...",
            validation_error_en="Please select your qualification.",
            validation_error_hi="कृपया अपनी योग्यता चुनें।",
            options=[
                QuestionOption("class_10", "10th Pass (High School)", "10वीं पास"),
                QuestionOption("class_12", "12th Pass (Higher Secondary)", "12वीं पास"),
                QuestionOption("iti", "ITI / Industrial Training Certificate", "आईटीआई प्रमाण पत्र"),
                QuestionOption("diploma", "Polytechnic Diploma", "पॉलिटेक्निक डिप्लोमा"),
                QuestionOption("graduate", "Graduate / Bachelor's Degree (BA, BSc, BCom, BTech)", "स्नातक डिग्री"),
                QuestionOption("postgraduate", "Post-Graduate (MA, MSc, MBA, MTech)", "स्नातकोत्तर डिग्री"),
            ],
        ),
        QuestionField(
            id="preferred_sector",
            label_en="Preferred Industry Sector",
            label_hi="पसंदीदा उद्योग क्षेत्र",
            widget_type="select",
            required=True,
            placeholder_en="Select industry...",
            placeholder_hi="उद्योग चुनें...",
            options=[
                QuestionOption("tech", "Information Technology & Software", "सूचना प्रौद्योगिकी एवं सॉफ्टवेयर"),
                QuestionOption("manufacturing", "Manufacturing & Automotive", "विनिर्माण एवं ऑटोमोबाइल"),
                QuestionOption("banking", "Banking, Financial Services & Insurance", "बैंकिंग एवं वित्तीय सेवाएं"),
                QuestionOption("healthcare", "Healthcare & Pharma", "स्वास्थ्य एवं फार्मा"),
                QuestionOption("retail", "Retail & Consumer Goods", "खुदरा एवं उपभोक्ता सामान"),
                QuestionOption("any", "Any Industry Opportunity", "कोई भी उद्योग अवसर"),
            ],
        ),
    ],
)

# Sector: Jobs & Employment
JOBS_GROUP = QuestionGroup(
    id="sector_jobs",
    title_en="Employment & Career Profile",
    title_hi="रोजगार एवं करियर प्रोफ़ाइल",
    subtitle_en="Public employment schemes target specific work experience and job seeker profiles.",
    subtitle_hi="सार्वजनिक रोजगार योजनाएं कार्य अनुभव और रोजगार स्थिति के अनुसार लागू होती हैं।",
    condition=lambda a: a.get("intent") == "jobs",
    fields=[
        QuestionField(
            id="employment_status",
            label_en="Current Employment Status",
            label_hi="वर्तमान रोजगार स्थिति",
            widget_type="radio",
            required=True,
            validation_error_en="Please select current employment status.",
            validation_error_hi="कृपया अपनी रोजगार स्थिति चुनें।",
            options=[
                QuestionOption("unemployed", "Actively Looking for Work (Unemployed)", "रोजगार की तलाश में (बेरोजगार)"),
                QuestionOption("daily_wage", "Daily Wage / Informal Laborer", "दैनिक वेतनभोगी / अनौपचारिक मजदूर"),
                QuestionOption("student_seeking_job", "Final Year Student / Fresh Graduate", "अंतिम वर्ष के छात्र / फ्रेशर"),
                QuestionOption("self_employed", "Self-Employed / Freelancer", "स्वरोजगार / फ्रीलांसर"),
            ],
        ),
        QuestionField(
            id="job_experience",
            label_en="Total Work Experience",
            label_hi="कुल कार्य अनुभव",
            widget_type="radio",
            required=True,
            validation_error_en="Please select work experience.",
            validation_error_hi="कृपया कार्य अनुभव चुनें।",
            options=[
                QuestionOption("fresher", "Fresher (0 - 1 year)", "फ्रेशर (0 - 1 वर्ष)"),
                QuestionOption("mid", "1 - 3 years", "1 - 3 वर्ष"),
                QuestionOption("experienced", "More than 3 years", "3 वर्ष से अधिक"),
            ],
        ),
    ],
)

# Sector: Skill Development & Training
SKILLS_GROUP = QuestionGroup(
    id="sector_skills",
    title_en="Skill Training Preferences",
    title_hi="कौशल प्रशिक्षण प्राथमिकताएं",
    subtitle_en="PMKVY and vocational programs provide free certified training in technical trades.",
    subtitle_hi="नि:शुल्क प्रमाणित तकनीकी एवं व्यावसायिक प्रशिक्षण हेतु अपनी रुचि चुनें।",
    condition=lambda a: a.get("intent") == "skills",
    fields=[
        QuestionField(
            id="skill_area",
            label_en="Area of Skill Interest",
            label_hi="कौशल रुचि का क्षेत्र",
            widget_type="select",
            required=True,
            placeholder_en="Select skill area...",
            placeholder_hi="कौशल क्षेत्र चुनें...",
            validation_error_en="Please select a skill area.",
            validation_error_hi="कृपया कौशल क्षेत्र चुनें।",
            options=[
                QuestionOption("it_digital", "Digital Skills, Web & Computer Hardware", "डिजिटल कौशल एवं कंप्यूटर"),
                QuestionOption("electric_solar", "Electrician, Solar & Power Technician", "इलेक्ट्रीशियन व सौर तकनीशियन"),
                QuestionOption("automotive", "Automotive Mechanic & Driving", "ऑटोमोबाइल मैकेनिक व ड्राइविंग"),
                QuestionOption("healthcare_aide", "Healthcare General Duty Assistant / Nursing Aide", "स्वास्थ्य सहायक"),
                QuestionOption("textiles", "Apparel, Tailoring & Handicrafts", "सिलाई, परिधान व हस्तशिल्प"),
                QuestionOption("construction", "Construction, Masonry & Plumbing", "निर्माण, प्लंबिंग व राजमिस्त्री"),
            ],
        ),
    ],
)

# Sector: Business & Entrepreneurship
BUSINESS_GROUP = QuestionGroup(
    id="sector_business",
    title_en="Business & Enterprise Profile",
    title_hi="व्यवसाय एवं उद्यम प्रोफ़ाइल",
    subtitle_en="MSME loans (Mudra, PMEGP, PM SVANidhi) require details on business stage and turnover.",
    subtitle_hi="मुद्रा, स्वनिधि व एमएसएमई ऋण हेतु व्यवसाय स्थिति और टर्नओवर का विवरण।",
    condition=lambda a: a.get("intent") == "business",
    fields=[
        QuestionField(
            id="business_stage",
            label_en="Business Stage",
            label_hi="व्यवसाय की वर्तमान स्थिति",
            widget_type="radio",
            required=True,
            validation_error_en="Please select business stage.",
            validation_error_hi="कृपया व्यवसाय स्थिति चुनें।",
            options=[
                QuestionOption("street_vendor", "Street Vendor / Mobile Hawker / Artisan", "रेहड़ी-पटरी वेंडर / कारीगर"),
                QuestionOption("planning", "Planning to Start a New Business / Startup", "नया व्यवसाय शुरू करने की योजना"),
                QuestionOption("running_micro", "Running an Existing Micro Enterprise / Shop", "मौजूदा सूक्ष्म उद्यम / दुकान"),
                QuestionOption("running_small", "Running a Small / Medium Enterprise (MSME)", "लघु या मध्यम उद्योग (MSME)"),
            ],
        ),
        QuestionField(
            id="funding_need",
            label_en="Loan / Capital Requirement",
            label_hi="आवश्यक ऋण या पूंजी राशि",
            widget_type="select",
            required=True,
            placeholder_en="Select capital need...",
            placeholder_hi="आवश्यक राशि चुनें...",
            validation_error_en="Please select capital requirement.",
            validation_error_hi="कृपया पूंजी आवश्यकता चुनें।",
            options=[
                QuestionOption("under_50k", "Micro Capital up to ₹50,000 (Shishu / SVANidhi)", "₹50,000 तक"),
                QuestionOption("50k_to_5lakh", "Small Loan ₹50,000 to ₹5,00,000 (Kishore)", "₹50,000 से ₹5 लाख"),
                QuestionOption("5lakh_to_20lakh", "Business Loan ₹5 Lakh to ₹20 Lakh (Tarun)", "₹5 लाख से ₹20 लाख"),
                QuestionOption("above_20lakh", "Above ₹20 Lakh (Large Expansion)", "₹20 लाख से अधिक"),
            ],
        ),
    ],
)

# Sector: Agriculture & Farming
AGRICULTURE_GROUP = QuestionGroup(
    id="sector_agriculture",
    title_en="Agricultural Details",
    title_hi="कृषि एवं भूमि विवरण",
    subtitle_en="PM-KISAN and farm subsidies depend on cultivable landholding size and agricultural activity.",
    subtitle_hi="पीएम-किसान और कृषि सब्सिडी हेतु भूमि स्वामित्व और खेती का विवरण।",
    condition=lambda a: a.get("intent") == "agriculture",
    fields=[
        QuestionField(
            id="farmer_type",
            label_en="Agricultural Role",
            label_hi="कृषि भूमिका",
            widget_type="radio",
            required=True,
            validation_error_en="Please select your farming role.",
            validation_error_hi="कृपया अपनी कृषि भूमिका चुनें।",
            options=[
                QuestionOption("landowner", "Landowning Cultivator / Farmer", "भूमिधारक किसान"),
                QuestionOption("tenant", "Tenant Farmer / Sharecropper", "बटाईदार / पट्टाधारक किसान"),
                QuestionOption("laborer", "Agricultural Laborer / Landless Farm Worker", "भूमिहीन कृषि मजदूर"),
            ],
        ),
        QuestionField(
            id="landholding_acres",
            label_en="Cultivable Land Size (in Acres)",
            label_hi="कृषि भूमि का आकार (एकड़ में)",
            help_en="Enter approximate agricultural land owned or cultivated (e.g. 2.5).",
            help_hi="स्वामित्व वाली या खेती योग्य भूमि एकड़ में दर्ज करें (उदा. 2.5)।",
            widget_type="number",
            required=False,
            min_value=0.0,
            max_value=500.0,
            step_value=0.5,
            placeholder_en="e.g. 2.0 (enter 0 if landless)",
            placeholder_hi="उदा. 2.0",
        ),
        QuestionField(
            id="crop_activity",
            label_en="Primary Farming Activity",
            label_hi="मुख्य कृषि गतिविधि",
            widget_type="select",
            required=True,
            placeholder_en="Select farming activity...",
            placeholder_hi="कृषि गतिविधि चुनें...",
            options=[
                QuestionOption("foodgrains", "Food Grains (Wheat, Rice, Pulses, Millets)", "अन्न व दालें"),
                QuestionOption("horticulture", "Vegetables, Fruits & Flowers (Horticulture)", "सब्जियां व बागवानी"),
                QuestionOption("dairy_livestock", "Dairy, Cattle & Livestock Farming", "डेयरी व पशुपालन"),
                QuestionOption("fisheries", "Fisheries & Aquaculture", "मत्स्य पालन"),
            ],
        ),
    ],
)

# Sector: Housing & Shelter
HOUSING_GROUP = QuestionGroup(
    id="sector_housing",
    title_en="Current Housing Situation",
    title_hi="आवास की वर्तमान स्थिति",
    subtitle_en="PMAY grants are targeted at houseless families and dilapidated kutcha houses.",
    subtitle_hi="पीएम आवास योजना कच्चे और बेघर परिवारों को पक्के मकान हेतु सहायता देती है।",
    condition=lambda a: a.get("intent") == "housing",
    fields=[
        QuestionField(
            id="housing_status",
            label_en="Current Dwelling Type",
            label_hi="वर्तमान मकान का प्रकार",
            widget_type="radio",
            required=True,
            validation_error_en="Please select your current dwelling type.",
            validation_error_hi="कृपया अपने मकान का प्रकार चुनें।",
            options=[
                QuestionOption("homeless", "Houseless / No Permanent Shelter", "बेघर / कोई स्थाई आश्रय नहीं"),
                QuestionOption("kutcha", "Kutcha House (Mud / Thatch / Dilapidated Roof)", "कच्चा मकान / जीर्ण-शीर्ण"),
                QuestionOption("rented", "Rented Accommodation", "किराए का मकान"),
                QuestionOption("pucca", "Own Pucca House", "स्वयं का पक्का मकान"),
            ],
        ),
        QuestionField(
            id="land_for_house",
            label_en="Do you own land/patta to construct a house?",
            label_hi="क्या आपके पास मकान निर्माण हेतु अपनी जमीन या पट्टा है?",
            widget_type="radio",
            required=True,
            validation_error_en="Please select land ownership status.",
            validation_error_hi="कृपया जमीन स्वामित्व स्थिति चुनें।",
            options=[
                QuestionOption("yes", "Yes, own land / residential patta available", "हाँ, जमीन या पट्टा उपलब्ध है"),
                QuestionOption("no", "No, landless", "नहीं, भूमिहीन हैं"),
            ],
        ),
    ],
)

# Sector: Healthcare
HEALTHCARE_GROUP = QuestionGroup(
    id="sector_healthcare",
    title_en="Healthcare Assistance Need",
    title_hi="स्वास्थ्य सहायता की आवश्यकता",
    subtitle_en="Ayushman Bharat covers hospitalization and treatment across empaneled hospitals.",
    subtitle_hi="आयुष्मान भारत पैनलबद्ध अस्पतालों में कैशलेस भर्ती और उपचार प्रदान करता है।",
    condition=lambda a: a.get("intent") == "healthcare",
    fields=[
        QuestionField(
            id="health_need",
            label_en="Healthcare Requirement",
            label_hi="स्वास्थ्य सहायता की प्रकृति",
            widget_type="radio",
            required=True,
            validation_error_en="Please select healthcare need.",
            validation_error_hi="कृपया स्वास्थ्य सहायता प्रकार चुनें।",
            options=[
                QuestionOption("hospitalization", "In-patient Hospitalization / Surgery Coverage (Ayushman Card)", "अस्पताल में भर्ती व सर्जरी सहायता"),
                QuestionOption("critical_illness", "Critical Illness (Cancer, Kidney, Cardiac) Relief", "गंभीर बीमारी उपचार राहत"),
                QuestionOption("maternal", "Maternal Care / Institutional Delivery", "मातृत्व व प्रसव सहायता"),
                QuestionOption("generic_medicine", "Affordable Generic Medicines (Jan Aushadhi)", "सस्ती दवाएं (जन औषधि)"),
            ],
        ),
    ],
)

# Sector: Women & Child
WOMEN_CHILD_GROUP = QuestionGroup(
    id="sector_women_child",
    title_en="Women & Child Assistance Profile",
    title_hi="महिला एवं बाल विकास सहायता",
    subtitle_en="Schemes for girl child future savings, pregnant mothers, and women empowerment.",
    subtitle_hi="बालिका बचत, गर्भवती महिलाओं और महिला सशक्तिकरण हेतु योजनाएं।",
    condition=lambda a: a.get("intent") == "women_child",
    fields=[
        QuestionField(
            id="women_target_need",
            label_en="Specific Scheme Focus",
            label_hi="विशिष्ट योजना का उद्देश्य",
            widget_type="radio",
            required=True,
            validation_error_en="Please select scheme focus.",
            validation_error_hi="कृपया योजना का उद्देश्य चुनें।",
            options=[
                QuestionOption("girl_savings", "Girl Child Savings & Higher Education (Sukanya Samriddhi)", "सुकन्या समृद्धि बालिका बचत"),
                QuestionOption("maternity", "Pregnant / Lactating Mother Support (Matru Vandana)", "मातृत्व पोषण सहायता"),
                QuestionOption("widow_support", "Single Mother / Widow Welfare & Pension", "एकल महिला / विधवा सहायता"),
                QuestionOption("livelihood", "Women Self-Help Group (SHG) & Enterprise Loan", "महिला स्वयं सहायता समूह ऋण"),
            ],
        ),
    ],
)

# Sector: Senior Citizens & Pension
PENSION_GROUP = QuestionGroup(
    id="sector_pension",
    title_en="Senior Citizen & Pension Details",
    title_hi="वरिष्ठ नागरिक एवं पेंशन विवरण",
    subtitle_en="Non-contributory old age pensions and social security schemes.",
    subtitle_hi="वृद्धावस्था पेंशन और सामाजिक सुरक्षा योजनाएं।",
    condition=lambda a: a.get("intent") == "pension",
    fields=[
        QuestionField(
            id="pension_status",
            label_en="Current Pension Coverage",
            label_hi="वर्तमान पेंशन स्थिति",
            widget_type="radio",
            required=True,
            validation_error_en="Please select current pension coverage.",
            validation_error_hi="कृपया पेंशन स्थिति चुनें।",
            options=[
                QuestionOption("no_pension", "Not receiving any government or private pension", "कोई पेंशन प्राप्त नहीं हो रही"),
                QuestionOption("unorganized_worker", "Unorganized Sector Worker seeking Atal Pension (APY)", "असंगठित क्षेत्र के कामगार"),
                QuestionOption("existing_pensioner", "Already receiving partial pension", "पहले से पेंशन प्राप्त हो रही है"),
            ],
        ),
    ],
)

# Sector: Disability Support
DISABILITY_GROUP = QuestionGroup(
    id="sector_disability",
    title_en="Disability Support Requirements",
    title_hi="दिव्यांगजन सहायता आवश्यकता",
    subtitle_en="NHFDC concessional loans, assistive devices, and disability pensions.",
    subtitle_hi="रियायती स्वरोजगार ऋण, सहायक उपकरण और दिव्यांग पेंशन योजनाएं।",
    condition=lambda a: a.get("intent") == "disability",
    fields=[
        QuestionField(
            id="disability_support_need",
            label_en="Primary Assistance Needed",
            label_hi="प्राथमिक सहायता की आवश्यकता",
            widget_type="radio",
            required=True,
            validation_error_en="Please select assistance needed.",
            validation_error_hi="कृपया आवश्यक सहायता चुनें।",
            options=[
                QuestionOption("self_employment", "Concessional Self-Employment / Business Loan (NHFDC)", "स्वरोजगार हेतु रियायती ऋण"),
                QuestionOption("assistive_device", "Assistive Devices & Mobility Equipment (ADIP)", "सहायक उपकरण एवं व्हीलचेयर"),
                QuestionOption("pension", "Disability Pension Assistance", "दिव्यांग पेंशन सहायता"),
                QuestionOption("skill_training", "Vocational & Skill Training for PwD", "व्यावसायिक प्रशिक्षण"),
            ],
        ),
    ],
)


ALL_SECTOR_GROUPS: List[QuestionGroup] = [
    EDUCATION_GROUP,
    INTERNSHIP_GROUP,
    JOBS_GROUP,
    SKILLS_GROUP,
    BUSINESS_GROUP,
    AGRICULTURE_GROUP,
    HOUSING_GROUP,
    HEALTHCARE_GROUP,
    WOMEN_CHILD_GROUP,
    PENSION_GROUP,
    DISABILITY_GROUP,
]


class QuestionnaireEngine:
    """Manages grouped question progression, validation, and canonical profile synchronization."""

    def __init__(self):
        self.intent_group = INTENT_GROUP
        self.common_groups = [LOCATION_PERSONAL_GROUP, ECONOMIC_SOCIAL_GROUP]
        self.sector_groups = ALL_SECTOR_GROUPS

    def get_active_groups(self, answers: Dict[str, Any]) -> List[QuestionGroup]:
        """Returns the ordered list of active question groups for the current session."""
        groups = [self.intent_group]
        # Only show common and sector groups once intent is selected
        if answers.get("intent"):
            groups.extend(self.common_groups)
            for sg in self.sector_groups:
                if sg.condition is None or sg.condition(answers):
                    groups.append(sg)
        return groups

    def validate_field(
        self,
        q_field: QuestionField,
        value: Any,
        lang: str = "en",
    ) -> Tuple[bool, Optional[str]]:
        """Validates an individual field value."""
        if not q_field.required and (value is None or value == ""):
            return True, None

        if q_field.required:
            if value is None or value == "" or str(value).strip().lower() in ("select", "none"):
                err = q_field.validation_error_hi if lang == "hi" else q_field.validation_error_en
                return False, err or ("कृपया यह जानकारी भरें।" if lang == "hi" else f"Please complete {q_field.label_en}.")

        if q_field.widget_type == "number":
            try:
                num = float(value)
                if q_field.min_value is not None and num < q_field.min_value:
                    return False, f"Minimum value is {q_field.min_value:,.0f}"
                if q_field.max_value is not None and num > q_field.max_value:
                    return False, f"Maximum value is {q_field.max_value:,.0f}"
            except (ValueError, TypeError):
                return False, "Please enter a valid numeric amount."

        return True, None

    def validate_group(
        self,
        group: QuestionGroup,
        answers: Dict[str, Any],
        lang: str = "en",
    ) -> Tuple[bool, Optional[str]]:
        """Validates all fields within an active question group."""
        for f in group.fields:
            if f.condition is not None and not f.condition(answers):
                continue
            val = answers.get(f.id)
            is_valid, err_msg = self.validate_field(f, val, lang=lang)
            if not is_valid:
                return False, err_msg
        return True, None

    def build_profile_payload(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes answers dictionary into canonical citizen profile payload."""
        income_val = answers.get("annual_income")
        if income_val is not None:
            try:
                income_val = float(income_val)
            except (ValueError, TypeError):
                income_val = None

        age_val = answers.get("age")
        if age_val is not None:
            try:
                age_val = int(age_val)
            except (ValueError, TypeError):
                age_val = None

        disability_bool = str(answers.get("disability", "")).lower() == "yes"
        minority_bool = str(answers.get("minority_status", "")).lower() == "yes"

        # Determine occupation and intent
        intent = answers.get("intent", "general")
        occupation = answers.get("occupation")
        if not occupation:
            if intent == "education":
                occupation = "student"
            elif intent == "agriculture":
                occupation = "farmer"
            elif intent == "business":
                occupation = "entrepreneur"
            elif intent in ("internships", "skills"):
                occupation = "student"

        # Build structured sector objects
        education_dict = {}
        if intent == "education" or answers.get("education_level"):
            education_dict = {
                "level": answers.get("education_level"),
                "course": answers.get("course_name"),
                "institution_type": answers.get("institution_type"),
            }

        business_dict = {}
        if intent == "business" or answers.get("business_stage"):
            business_dict = {
                "stage": answers.get("business_stage"),
                "funding_need": answers.get("funding_need"),
            }

        agriculture_dict = {}
        if intent == "agriculture" or answers.get("farmer_type"):
            agriculture_dict = {
                "role": answers.get("farmer_type"),
                "landholding_acres": answers.get("landholding_acres"),
                "crop_activity": answers.get("crop_activity"),
            }

        return {
            "state": answers.get("state"),
            "district": answers.get("district"),
            "age": age_val,
            "gender": answers.get("gender"),
            "marital_status": answers.get("marital_status"),
            "annual_income": income_val,
            "annual_family_income": income_val,
            "occupation": occupation,
            "employment_status": answers.get("employment_status"),
            "category": answers.get("social_category"),
            "area": answers.get("area"),
            "residence_type": answers.get("area"),
            "disability": disability_bool,
            "minority_status": minority_bool,
            "intent": intent,
            "needs": [intent],
            "education": education_dict,
            "business": business_dict,
            "agriculture": agriculture_dict,
            "dynamic_answers": dict(answers),
        }


questionnaire_engine = QuestionnaireEngine()
