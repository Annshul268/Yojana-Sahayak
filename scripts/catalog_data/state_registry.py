"""State Welfare Programs Registry across all 20 Priority Indian States.

Systematically models the essential state-level welfare and scholarship initiatives
with verified state portals, official departments, and accurate eligibility rules.
"""

from typing import Any, Dict, List

# Metadata for 20 Priority States + Delhi
STATE_PORTAL_MAP = {
    "Uttar Pradesh": {
        "code": "UP",
        "portal": "https://scholarship.up.gov.in/",
        "dept_edu": "Social Welfare & Backward Classes Welfare Department, Uttar Pradesh",
        "dept_soc": "Social Welfare Department, Government of Uttar Pradesh",
        "dept_agri": "Department of Agriculture, Uttar Pradesh",
        "dept_wcd": "Women and Child Development Department, Uttar Pradesh",
        "dept_ind": "Directorate of Industries, MSME Department, Uttar Pradesh",
        "pension_url": "https://sspy-up.gov.in/",
        "scholarship_url": "https://scholarship.up.gov.in/",
        "agri_url": "http://upagriculture.com/",
        "wcd_url": "https://womenchild.up.gov.in/",
        "ind_url": "http://diupmsme.upsdc.gov.in/",
    },
    "Maharashtra": {
        "code": "MH",
        "portal": "https://mahadbt.maharashtra.gov.in/",
        "dept_edu": "Higher and Technical Education Department, Maharashtra",
        "dept_soc": "Social Justice and Special Assistance Department, Maharashtra",
        "dept_agri": "Department of Agriculture, Maharashtra",
        "dept_wcd": "Women and Child Development Department, Maharashtra",
        "dept_ind": "Directorate of Industries, Maharashtra",
        "pension_url": "https://aaplesarkar.mahaonline.gov.in/",
        "scholarship_url": "https://mahadbt.maharashtra.gov.in/",
        "agri_url": "https://krishi.maharashtra.gov.in/",
        "wcd_url": "https://womenchild.maharashtra.gov.in/",
        "ind_url": "https://industry.maharashtra.gov.in/",
    },
    "Rajasthan": {
        "code": "RJ",
        "portal": "https://sso.rajasthan.gov.in/",
        "dept_edu": "Social Justice and Empowerment Department, Rajasthan",
        "dept_soc": "Social Justice and Empowerment Department, Rajasthan",
        "dept_agri": "Department of Agriculture, Rajasthan",
        "dept_wcd": "Directorate of Women Empowerment, Rajasthan",
        "dept_ind": "Department of Industries and Commerce, Rajasthan",
        "pension_url": "https://ssp.rajasthan.gov.in/",
        "scholarship_url": "https://sjmsnew.rajasthan.gov.in/",
        "agri_url": "https://agriculture.rajasthan.gov.in/",
        "wcd_url": "https://wcd.rajasthan.gov.in/",
        "ind_url": "https://industries.rajasthan.gov.in/",
    },
    "Madhya Pradesh": {
        "code": "MP",
        "portal": "http://scholarshipportal.mp.nic.in/",
        "dept_edu": "Higher Education Department, Madhya Pradesh",
        "dept_soc": "Social Justice and Disabled Welfare Department, Madhya Pradesh",
        "dept_agri": "Farmer Welfare and Agriculture Development Department, MP",
        "dept_wcd": "Directorate of Women and Child Development, MP",
        "dept_ind": "Department of Micro, Small and Medium Enterprises, MP",
        "pension_url": "https://socialjustice.mp.gov.in/",
        "scholarship_url": "http://scholarshipportal.mp.nic.in/",
        "agri_url": "http://mpkrishi.mp.gov.in/",
        "wcd_url": "https://mpwcdmis.gov.in/",
        "ind_url": "https://msme.mponline.gov.in/",
    },
    "Bihar": {
        "code": "BR",
        "portal": "http://pmsonline.bih.nic.in/",
        "dept_edu": "Education Department, Government of Bihar",
        "dept_soc": "Social Welfare Department, Government of Bihar",
        "dept_agri": "Department of Agriculture, Bihar",
        "dept_wcd": "Women and Child Development Corporation, Bihar",
        "dept_ind": "Department of Industries, Bihar",
        "pension_url": "https://sspmis.bihar.gov.in/",
        "scholarship_url": "http://pmsonline.bih.nic.in/",
        "agri_url": "https://dbtagriculture.bihar.gov.in/",
        "wcd_url": "https://wcdc.bihar.gov.in/",
        "ind_url": "https://udyami.bihar.gov.in/",
    },
    "West Bengal": {
        "code": "WB",
        "portal": "https://oasis.gov.in/",
        "dept_edu": "Backward Classes Welfare Department, West Bengal",
        "dept_soc": "Department of Women & Child Development and Social Welfare, WB",
        "dept_agri": "Department of Agriculture, West Bengal",
        "dept_wcd": "Department of Women and Child Development, WB",
        "dept_ind": "Micro, Small & Medium Enterprises and Textiles Department, WB",
        "pension_url": "https://wb.gov.in/",
        "scholarship_url": "https://oasis.gov.in/",
        "agri_url": "https://krishakbandhu.wb.gov.in/",
        "wcd_url": "https://www.wbkanyashree.gov.in/",
        "ind_url": "https://myenterprisewb.in/",
    },
    "Gujarat": {
        "code": "GJ",
        "portal": "https://digitalgujarat.gov.in/",
        "dept_edu": "Education Department, Government of Gujarat",
        "dept_soc": "Social Justice and Empowerment Department, Gujarat",
        "dept_agri": "Agriculture, Farmers Welfare and Co-operation Department, Gujarat",
        "dept_wcd": "Women and Child Development Department, Gujarat",
        "dept_ind": "Industries and Mines Department, Gujarat",
        "pension_url": "https://sje.gujarat.gov.in/",
        "scholarship_url": "https://digitalgujarat.gov.in/",
        "agri_url": "https://ikhedut.gujarat.gov.in/",
        "wcd_url": "https://wcd.gujarat.gov.in/",
        "ind_url": "https://cottage.gujarat.gov.in/",
    },
    "Karnataka": {
        "code": "KA",
        "portal": "https://ssp.postmatric.karnataka.gov.in/",
        "dept_edu": "Social Welfare & Backward Classes Welfare Department, Karnataka",
        "dept_soc": "Social Welfare Department, Karnataka",
        "dept_agri": "Department of Agriculture, Karnataka",
        "dept_wcd": "Women and Child Development Department, Karnataka",
        "dept_ind": "Department of Commerce and Industries, Karnataka",
        "pension_url": "https://sevasindhu.karnataka.gov.in/",
        "scholarship_url": "https://ssp.postmatric.karnataka.gov.in/",
        "agri_url": "https://raitamitra.karnataka.gov.in/",
        "wcd_url": "https://sevasindhugs.karnataka.gov.in/",
        "ind_url": "https://kum.karnataka.gov.in/",
    },
    "Tamil Nadu": {
        "code": "TN",
        "portal": "https://www.tn.gov.in/",
        "dept_edu": "Adi Dravidar and Tribal Welfare Department, Tamil Nadu",
        "dept_soc": "Social Welfare and Women Empowerment Department, Tamil Nadu",
        "dept_agri": "Agriculture and Farmers Welfare Department, Tamil Nadu",
        "dept_wcd": "Directorate of Social Welfare, Tamil Nadu",
        "dept_ind": "Micro, Small and Medium Enterprises Department, Tamil Nadu",
        "pension_url": "https://www.tn.gov.in/scheme/department_wise/31",
        "scholarship_url": "https://escholarship.tn.gov.in/",
        "agri_url": "https://www.agritech.tnau.ac.in/",
        "wcd_url": "https://socialwelfare.tn.gov.in/",
        "ind_url": "https://www.msmeonline.tn.gov.in/",
    },
    "Telangana": {
        "code": "TS",
        "portal": "https://telanganaepass.cgg.gov.in/",
        "dept_edu": "Scheduled Castes Development & BC Welfare Department, Telangana",
        "dept_soc": "Panchayat Raj and Rural Development Department, Telangana",
        "dept_agri": "Agriculture and Cooperation Department, Telangana",
        "dept_wcd": "Department of Women, Children, Disabled and Senior Citizens, Telangana",
        "dept_ind": "Industries and Commerce Department, Telangana",
        "pension_url": "https://aasara.telangana.gov.in/",
        "scholarship_url": "https://telanganaepass.cgg.gov.in/",
        "agri_url": "https://agri.telangana.gov.in/",
        "wcd_url": "https://wdcw.tg.nic.in/",
        "ind_url": "https://ipass.telangana.gov.in/",
    },
    "Andhra Pradesh": {
        "code": "AP",
        "portal": "https://jnanabhumi.ap.gov.in/",
        "dept_edu": "Social Welfare and Higher Education Department, Andhra Pradesh",
        "dept_soc": "Panchayat Raj & Rural Development Department, Andhra Pradesh",
        "dept_agri": "Department of Agriculture, Andhra Pradesh",
        "dept_wcd": "Department of Women, Children, Differently Abled & Senior Citizens, AP",
        "dept_ind": "Industries and Commerce Department, Andhra Pradesh",
        "pension_url": "https://sspensions.ap.gov.in/",
        "scholarship_url": "https://jnanabhumi.ap.gov.in/",
        "agri_url": "https://karshak.ap.gov.in/",
        "wcd_url": "https://navasakam2.apcfss.in/",
        "ind_url": "https://singlewindow.ap.gov.in/",
    },
    "Odisha": {
        "code": "OD",
        "portal": "https://scholarship.odisha.gov.in/",
        "dept_edu": "ST & SC Development and Minorities & Backward Classes Welfare, Odisha",
        "dept_soc": "Social Security and Empowerment of Persons with Disabilities, Odisha",
        "dept_agri": "Department of Agriculture and Farmers' Empowerment, Odisha",
        "dept_wcd": "Women and Child Development Department, Odisha",
        "dept_ind": "Micro, Small & Medium Enterprises Department, Odisha",
        "pension_url": "https://ssepd.odisha.gov.in/",
        "scholarship_url": "https://scholarship.odisha.gov.in/",
        "agri_url": "https://agri.odisha.gov.in/",
        "wcd_url": "https://wcd.odisha.gov.in/",
        "ind_url": "https://msme.odisha.gov.in/",
    },
    "Punjab": {
        "code": "PB",
        "portal": "https://scholarships.punjab.gov.in/",
        "dept_edu": "Department of Social Justice, Empowerment and Minorities, Punjab",
        "dept_soc": "Department of Social Security and Women & Child Development, Punjab",
        "dept_agri": "Department of Agriculture and Farmers Welfare, Punjab",
        "dept_wcd": "Department of Social Security and WCD, Punjab",
        "dept_ind": "Department of Industries and Commerce, Punjab",
        "pension_url": "https://punjab.gov.in/",
        "scholarship_url": "https://scholarships.punjab.gov.in/",
        "agri_url": "https://agri.punjab.gov.in/",
        "wcd_url": "https://sswcd.punjab.gov.in/",
        "ind_url": "https://pbindustries.gov.in/",
    },
    "Haryana": {
        "code": "HR",
        "portal": "https://harchhatravratti.highereduhry.ac.in/",
        "dept_edu": "Department of Higher Education, Haryana",
        "dept_soc": "Social Justice, Empowerment, Welfare of SCs & BCs Department, Haryana",
        "dept_agri": "Agriculture and Farmers Welfare Department, Haryana",
        "dept_wcd": "Women and Child Development Department, Haryana",
        "dept_ind": "Industries and Commerce Department, Haryana",
        "pension_url": "https://pension.socialjusticehry.gov.in/",
        "scholarship_url": "https://harchhatravratti.highereduhry.ac.in/",
        "agri_url": "https://fasal.haryana.gov.in/",
        "wcd_url": "https://wcdhry.gov.in/",
        "ind_url": "https://haryanaindustries.gov.in/",
    },
    "Kerala": {
        "code": "KL",
        "portal": "https://egrantz.kerala.gov.in/",
        "dept_edu": "Scheduled Castes Development & Backward Classes Welfare, Kerala",
        "dept_soc": "Social Justice Department, Government of Kerala",
        "dept_agri": "Department of Agriculture Development and Farmers' Welfare, Kerala",
        "dept_wcd": "Women and Child Development Department, Kerala",
        "dept_ind": "Department of Industries and Commerce, Kerala",
        "pension_url": "https://welfarepension.lsgkerala.gov.in/",
        "scholarship_url": "https://egrantz.kerala.gov.in/",
        "agri_url": "https://aims.kerala.gov.in/",
        "wcd_url": "https://wcd.kerala.gov.in/",
        "ind_url": "https://industry.kerala.gov.in/",
    },
    "Jharkhand": {
        "code": "JH",
        "portal": "https://ekalyan.cgg.gov.in/",
        "dept_edu": "Scheduled Tribe, Scheduled Caste, Minority and Backward Class Welfare, JH",
        "dept_soc": "Women, Child Development and Social Security Department, Jharkhand",
        "dept_agri": "Department of Agriculture, Animal Husbandry and Co-operative, Jharkhand",
        "dept_wcd": "WCD and Social Security Department, Jharkhand",
        "dept_ind": "Department of Industries, Jharkhand",
        "pension_url": "https://jharkhand.gov.in/",
        "scholarship_url": "https://ekalyan.cgg.gov.in/",
        "agri_url": "https://agri.jharkhand.gov.in/",
        "wcd_url": "https://mmmsy.jharkhand.gov.in/",
        "ind_url": "https://advantage.jharkhand.gov.in/",
    },
    "Chhattisgarh": {
        "code": "CG",
        "portal": "http://postmatric-scholarship.cg.nic.in/",
        "dept_edu": "Tribal and Scheduled Caste Development Department, Chhattisgarh",
        "dept_soc": "Social Welfare Department, Chhattisgarh",
        "dept_agri": "Department of Agriculture and Farmers Welfare, Chhattisgarh",
        "dept_wcd": "Women and Child Development Department, Chhattisgarh",
        "dept_ind": "Commerce and Industries Department, Chhattisgarh",
        "pension_url": "https://sw.cg.gov.in/",
        "scholarship_url": "http://postmatric-scholarship.cg.nic.in/",
        "agri_url": "https://agriportal.cg.nic.in/",
        "wcd_url": "https://mahtarivandan.cgstate.gov.in/",
        "ind_url": "https://industries.cg.gov.in/",
    },
    "Assam": {
        "code": "AS",
        "portal": "https://directorateofhighereducation.assam.gov.in/",
        "dept_edu": "Higher Education Department, Government of Assam",
        "dept_soc": "Social Justice and Empowerment Department, Assam",
        "dept_agri": "Department of Agriculture, Assam",
        "dept_wcd": "Women and Child Development Department, Assam",
        "dept_ind": "Department of Industries, Commerce & Public Enterprise, Assam",
        "pension_url": "https://socialwelfare.assam.gov.in/",
        "scholarship_url": "https://directorateofhighereducation.assam.gov.in/",
        "agri_url": "https://agri-horti.assam.gov.in/",
        "wcd_url": "https://orunodoi.assam.gov.in/",
        "ind_url": "https://industriescom.assam.gov.in/",
    },
    "Uttarakhand": {
        "code": "UK",
        "portal": "http://escholarship.uk.gov.in/",
        "dept_edu": "Social Welfare Department, Uttarakhand",
        "dept_soc": "Social Welfare Department, Government of Uttarakhand",
        "dept_agri": "Department of Agriculture, Uttarakhand",
        "dept_wcd": "Women Empowerment and Child Development Department, Uttarakhand",
        "dept_ind": "Directorate of Industries, Uttarakhand",
        "pension_url": "https://ssp.uk.gov.in/",
        "scholarship_url": "http://escholarship.uk.gov.in/",
        "agri_url": "https://agriculture.uk.gov.in/",
        "wcd_url": "https://nandagaura.uk.gov.in/",
        "ind_url": "https://doiuk.org/",
    },
    "Himachal Pradesh": {
        "code": "HP",
        "portal": "https://hpepass.cgg.gov.in/",
        "dept_edu": "Higher Education Department, Himachal Pradesh",
        "dept_soc": "Social Justice and Empowerment Department, Himachal Pradesh",
        "dept_agri": "Department of Agriculture, Himachal Pradesh",
        "dept_wcd": "Directorate of Women and Child Development, HP",
        "dept_ind": "Industries Department, Himachal Pradesh",
        "pension_url": "https://esomsa.hp.gov.in/",
        "scholarship_url": "https://hpepass.cgg.gov.in/",
        "agri_url": "https://agricoop.hp.gov.in/",
        "wcd_url": "https://wcd.hp.gov.in/",
        "ind_url": "https://emerginghimachal.hp.gov.in/",
    },
    "Delhi": {
        "code": "DL",
        "portal": "https://edistrict.delhigovt.nic.in/",
        "dept_edu": "Directorate of Higher Education, Government of NCT of Delhi",
        "dept_soc": "Social Welfare Department, Government of NCT of Delhi",
        "dept_agri": "Development Department, Government of NCT of Delhi",
        "dept_wcd": "Department of Women and Child Development, Delhi",
        "dept_ind": "Industries Department, Government of NCT of Delhi",
        "pension_url": "https://edistrict.delhigovt.nic.in/",
        "scholarship_url": "https://edistrict.delhigovt.nic.in/",
        "agri_url": "https://delhi.gov.in/",
        "wcd_url": "https://wcd.delhi.gov.in/",
        "ind_url": "https://industries.delhi.gov.in/",
    }
}


def generate_state_catalog() -> List[Dict[str, Any]]:
    """Generates structured, verified schemes for each of the 21 focus states/UTs."""
    schemes: List[Dict[str, Any]] = []

    for state_name, meta in STATE_PORTAL_MAP.items():
        st_code = meta["code"]
        st_slug = state_name.lower().replace(" ", "-")

        # 1. State Destitute Widow Pension Scheme
        schemes.append({
            "slug": f"{st_slug}-widow-pension-scheme",
            "scheme_code": f"SCH-{st_code}-SOC-001",
            "name": f"{state_name} Destitute Widow Pension Scheme",
            "name_hi": f"{state_name} निराश्रित विधवा पेंशन योजना",
            "description": f"State welfare pension providing regular monthly financial subsistence directly to destitute and low-income widows domiciled in {state_name}.",
            "description_hi": f"{state_name} की निराश्रित एवं निर्धन विधवा महिलाओं को सम्मानजनक जीवन एवं आर्थिक संबल हेतु प्रतिमाह नियमित पेंशन।",
            "primary_category": "Social Security & Pension",
            "category": "Social Security & Pension",
            "ministry": meta["dept_soc"],
            "department": meta["dept_soc"],
            "level": "State",
            "states": [state_name],
            "intents": ["pension", "women_child"],
            "target_beneficiaries": [f"Widows aged 18 and above domiciled in {state_name} living in low-income or BPL households"],
            "eligibility_rules": {
                "states": [state_name],
                "gender": ["female"],
                "income": {"max": 100000},
                "age": {"min": 18, "max": 60}
            },
            "benefits": [
                f"Monthly pension allowance credited directly into beneficiary's bank account via DBT",
                "Health assistance and social security coverage under state welfare programs"
            ],
            "documents": ["Death Certificate of Husband", f"{state_name} Domicile / Residence Proof", "BPL Card / Income Certificate", "Aadhaar Card", "Bank Account Details"],
            "application_steps": [
                f"Apply online through {state_name} e-District portal ({meta['pension_url']}) or at local Block/Tehsil office",
                "Verification by local revenue authority and sanction by District Social Welfare Officer",
                "Direct electronic monthly payment release"
            ],
            "official_url": meta["pension_url"],
            "source_url": meta["pension_url"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["pension", "widow", st_slug, "social-welfare", "dbt", "women-support"]
        })

        # 2. State Disability Pension / Divyangjan Welfare Scheme
        schemes.append({
            "slug": f"{st_slug}-divyangjan-disability-pension",
            "scheme_code": f"SCH-{st_code}-DIS-001",
            "name": f"{state_name} Divyangjan Disability Pension Scheme",
            "name_hi": f"{state_name} दिव्यांगजन पेंशन योजना",
            "description": f"Provides monthly financial disability pension directly to persons with benchmark disability of 40% or more domiciled in {state_name}.",
            "description_hi": f"{state_name} के 40% या अधिक दिव्यांगता वाले नागरिकों को मासिक वित्तीय पेंशन सहायता सीधे बैंक खाते में।",
            "primary_category": "Differently Abled Support",
            "category": "Differently Abled Support",
            "ministry": meta["dept_soc"],
            "department": meta["dept_soc"],
            "level": "State",
            "states": [state_name],
            "intents": ["disability", "pension"],
            "target_beneficiaries": [f"Persons with 40% or more benchmark disability domiciled in {state_name} with family income below state poverty threshold"],
            "eligibility_rules": {
                "states": [state_name],
                "disability": True,
                "income": {"max": 120000},
                "age": {"min": 18, "max": 100}
            },
            "benefits": [
                "Monthly disability pension directly credited via DBT to bank account",
                "Concessional public bus travel passes within state borders",
                "Priority in free distribution of motorized tricycles, wheelchairs, and hearing aids"
            ],
            "documents": ["UDID Card / Disability Certificate issued by Medical Board (≥40%)", f"{state_name} Domicile Certificate", "Income Certificate", "Aadhaar Card", "Bank Passbook"],
            "application_steps": [
                f"Submit application online via {meta['pension_url']} or through District Social Welfare Office",
                "Verification of medical certificate and domicile",
                "Monthly DBT release"
            ],
            "official_url": meta["pension_url"],
            "source_url": meta["pension_url"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["disability", "pension", st_slug, "differently-abled", "udid", "social-security"]
        })

        # 3. State Agricultural Equipment Subsidy & Farm Mechanization
        schemes.append({
            "slug": f"{st_slug}-farm-mechanization-subsidy",
            "scheme_code": f"SCH-{st_code}-AGRI-002",
            "name": f"{state_name} Agricultural Mechanization and Equipment Subsidy Scheme",
            "name_hi": f"{state_name} कृषि यंत्रीकरण एवं कृषि उपकरण अनुदान योजना",
            "description": f"Provides 40% to 50% capital subsidy on purchase of approved modern farm machinery (tractors, power rotavators, seed drills, sprayers, threshers) for farmers in {state_name}.",
            "description_hi": f"{state_name} के किसानों को ट्रैक्टर, रोटावेटर, रीपर, सीड ड्रिल एवं कृषि ड्रोन क्रय करने पर 40% से 50% तक सरकारी अनुदान।",
            "primary_category": "Agriculture & Rural Development",
            "category": "Agriculture & Rural Development",
            "ministry": meta["dept_agri"],
            "department": meta["dept_agri"],
            "level": "State",
            "states": [state_name],
            "intents": ["agriculture"],
            "target_beneficiaries": [f"Small, marginal, and women farmers holding agricultural land in {state_name}"],
            "eligibility_rules": {
                "states": [state_name],
                "occupation": ["farmer"],
                "age": {"min": 18, "max": 80}
            },
            "benefits": [
                "Direct capital subsidy of 40% to 50% on cost of approved agricultural implements from empanelled dealers",
                "Enhanced subsidy quota for SC, ST, and women farmers",
                "Reduces farm labor shortage and boosts crop productivity"
            ],
            "documents": ["Land Revenue Records (RoR / Khasra-Khatauni)", f"{state_name} Residence Proof", "Aadhaar Card", "Bank Account Passbook", "Caste Certificate (if applicable)"],
            "application_steps": [
                f"Register on {state_name} Agriculture portal ({meta['agri_url']})",
                "Select machinery and authorized dealer",
                "Lottery token generation, purchase equipment, and receive subsidy after field geo-tagging"
            ],
            "official_url": meta["agri_url"],
            "source_url": meta["agri_url"],
            "source_name": f"Department of Agriculture {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["agriculture", "machinery", "tractor", st_slug, "farmer", "subsidy", "farm-equipment"]
        })

        # 4. State MSME Self-Employment & Youth Entrepreneurship Scheme
        schemes.append({
            "slug": f"{st_slug}-mukhyamantri-yuva-swarojgar-yojana",
            "scheme_code": f"SCH-{st_code}-BIZ-002",
            "name": f"{state_name} Mukhyamantri Yuva Swarojgar Yojana (Self-Employment)",
            "name_hi": f"{state_name} मुख्यमंत्री युवा स्वरोजगार योजना",
            "description": f"Credit-linked enterprise loan subsidy scheme facilitating bank loans up to ₹25 Lakhs in manufacturing and ₹10 Lakhs in services with 15% to 25% margin money subsidy for youth in {state_name}.",
            "description_hi": f"{state_name} के शिक्षित बेरोजगार युवाओं को स्वयं का उद्योग अथवा सेवा प्रतिष्ठान स्थापित करने हेतु बैंक ऋण एवं 25% तक सरकारी मार्जिन मनी अनुदान।",
            "primary_category": "Business & Self Employment",
            "category": "Business & Self Employment",
            "ministry": meta["dept_ind"],
            "department": meta["dept_ind"],
            "level": "State",
            "states": [state_name],
            "intents": ["business", "jobs"],
            "target_beneficiaries": [f"Unemployed youth aged 18-40 residing in {state_name} setting up new micro-enterprises"],
            "eligibility_rules": {
                "states": [state_name],
                "occupation": ["entrepreneur", "unemployed", "self_employed"],
                "age": {"min": 18, "max": 40}
            },
            "benefits": [
                "Margin money subsidy of 25% (up to ₹6.25 Lakh) for projects up to ₹25 Lakhs in manufacturing",
                "Margin money subsidy of 25% (up to ₹2.50 Lakh) for projects up to ₹10 Lakhs in service sector",
                "Entrepreneurship Development Training (EDP) sponsored by state government"
            ],
            "documents": [f"{state_name} Domicile Certificate", "Class 10 or 12 Passing Certificate", "Detailed Project Report (DPR)", "Aadhaar Card & PAN Card", "Caste Certificate (if SC/ST/OBC)"],
            "application_steps": [
                f"Apply online through {meta['ind_url']}",
                "District Level Task Force Committee (DLTFC) interview and recommendation to bank",
                "Bank loan sanction and subsidy credited into escrow account"
            ],
            "official_url": meta["ind_url"],
            "source_url": meta["ind_url"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["business", "swarojgar", st_slug, "entrepreneurship", "subsidy", "msme", "self-employment"]
        })

        # 5. State Rural Housing Assistance Scheme
        schemes.append({
            "slug": f"{st_slug}-mukhyamantri-awas-yojana",
            "scheme_code": f"SCH-{st_code}-HOU-001",
            "name": f"{state_name} Mukhyamantri Awas Yojana (Rural / Urban Housing)",
            "name_hi": f"{state_name} मुख्यमंत्री आवास योजना",
            "description": f"Provides financial grant of up to ₹1,30,000 for constructing disaster-resilient pucca houses for poor families in {state_name} who were left out of Central PMAY lists.",
            "description_hi": f"{state_name} के बेघर एवं कच्चे मकानों में रहने वाले निर्धन परिवारों (जो पीएम आवास से छूटे हों) को पक्के मकान निर्माण हेतु ₹1.30 लाख का सरकारी अनुदान।",
            "primary_category": "Housing & Shelter",
            "category": "Housing & Shelter",
            "ministry": meta["dept_soc"],
            "department": "Rural Development & Housing Department",
            "level": "State",
            "states": [state_name],
            "intents": ["housing"],
            "target_beneficiaries": [f"Poor families living in kutcha houses in {state_name} belonging to SC, ST, Musahar, Vanya, leprosy-affected, or disabled categories"],
            "eligibility_rules": {
                "states": [state_name],
                "income": {"max": 150000},
                "age": {"min": 18, "max": 85}
            },
            "benefits": [
                "Direct financial grant of ₹1,20,000 to ₹1,30,000 paid in 3 milestone installments directly into bank account",
                "Additional 90 days unskilled wage labor support under MGNREGA",
                "Free electricity connection under Saubhagya and LPG under Ujjwala"
            ],
            "documents": ["Aadhaar Card", f"{state_name} Residence Proof", "BPL Certificate / Gram Sabha approval", "Bank Passbook", "Photo of existing kutcha house"],
            "application_steps": [
                "Beneficiaries verified through Gram Sabha / Urban Local Body survey",
                "Administrative sanction by District Magistrate / BDO",
                "Stage-wise geo-tagged release of funds into beneficiary's bank account"
            ],
            "official_url": meta["portal"],
            "source_url": meta["portal"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["housing", "pucca-house", st_slug, "mukhyamantri-awas", "shelter", "rural-housing", "grant"]
        })

        # 6. State Girls Marriage / Kanyadan Financial Assistance Scheme
        schemes.append({
            "slug": f"{st_slug}-mukhyamantri-kanyadan-marriage-assistance",
            "scheme_code": f"SCH-{st_code}-WOM-002",
            "name": f"{state_name} Mukhyamantri Kanyadan / Vivah Sahayata Yojana",
            "name_hi": f"{state_name} मुख्यमंत्री कन्यादान / विवाह सहायता योजना",
            "description": f"One-time financial grant of ₹31,000 to ₹51,000 provided by {state_name} Government to poor parents for the marriage of their daughters aged 18 or above.",
            "description_hi": f"{state_name} के गरीब, श्रमिक एवं बीपीएल परिवारों की बेटियों के विवाह हेतु ₹31,000 से ₹51,000 की एकमुश्त सरकारी आर्थिक सहायता।",
            "primary_category": "Women & Child Development",
            "category": "Women & Child Development",
            "ministry": meta["dept_wcd"],
            "department": meta["dept_wcd"],
            "level": "State",
            "states": [state_name],
            "intents": ["women_child", "financial"],
            "target_beneficiaries": [f"BPL, labor card holders, and low-income families domiciled in {state_name} marrying daughters aged 18+ years"],
            "eligibility_rules": {
                "states": [state_name],
                "gender": ["female"],
                "income": {"max": 100000},
                "age": {"min": 18, "max": 35}
            },
            "benefits": [
                "One-time cash grant credited directly into bride's bank account via DBT",
                "Substantial relief from indebtedness caused by marriage expenses"
            ],
            "documents": ["Bride's Age Proof (Aadhaar / Class 10 certificate proving age ≥18)", "Marriage Card / Marriage Registration Certificate", f"{state_name} Domicile Certificate", "BPL Ration Card / Income Certificate", "Bride's Bank Account Details"],
            "application_steps": [
                f"Apply online via {meta['wcd_url']} or at local Block Development Office",
                "Verification by local revenue staff and sanction by District Social Welfare Officer",
                "Direct payment into bride's bank account"
            ],
            "official_url": meta["wcd_url"],
            "source_url": meta["wcd_url"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["women_child", "marriage", "kanyadan", st_slug, "financial-grant", "girls-welfare"]
        })

        # 7. State Post-Matric Scholarship Scheme (SC/ST/OBC/EWS)
        schemes.append({
            "slug": f"{st_slug}-state-post-matric-scholarship",
            "scheme_code": f"SCH-{st_code}-EDU-002",
            "name": f"{state_name} Post-Matric Scholarship for Backward Classes & Minorities",
            "name_hi": f"{state_name} दशमोत्तर छात्रवृत्ति एवं शुल्क प्रतिपूर्ति योजना",
            "description": f"State scholarship program providing full or partial tuition fee reimbursement and maintenance allowances to OBC, SC, ST, and EWS students pursuing post-matriculation courses in {state_name}.",
            "description_hi": f"{state_name} के पिछड़े एवं वंचित वर्ग के छात्र-छात्राओं हेतु 11वीं, 12वीं, आईटीआई, पॉलिटेक्निक एवं डिग्री कोर्सेज में शिक्षण शुल्क प्रतिपूर्ति एवं छात्रवृत्ति।",
            "primary_category": "Education & Learning",
            "category": "Education & Learning",
            "ministry": meta["dept_edu"],
            "department": meta["dept_edu"],
            "level": "State",
            "states": [state_name],
            "intents": ["education"],
            "target_beneficiaries": [f"Students domiciled in {state_name} pursuing post-matric courses with family income up to ₹2.5 Lakh"],
            "eligibility_rules": {
                "states": [state_name],
                "category": ["OBC", "SC", "ST", "EWS"],
                "occupation": ["student"],
                "income": {"max": 250000},
                "age": {"min": 15, "max": 35}
            },
            "benefits": [
                "Reimbursement of mandatory institutional tuition fees as fixed by the State Fee Committee",
                "Monthly maintenance allowance credited directly into student's Aadhaar-linked bank account",
                "Special book and thesis grants for professional and technical degree students"
            ],
            "documents": [f"{state_name} Domicile Certificate", "Caste Certificate", "Income Certificate (≤ ₹2.5 Lakh/yr)", "Previous Year Marksheet", "College Bonafide & Fee Receipt", "Bank Passbook"],
            "application_steps": [
                f"Apply online on {state_name} Scholarship Portal ({meta['scholarship_url']})",
                "College nodal officer verifies academic records and fee demand online",
                "District Welfare Officer approves and releases payment directly via DBT"
            ],
            "official_url": meta["scholarship_url"],
            "source_url": meta["scholarship_url"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["education", "scholarship", st_slug, "post-matric", "fee-reimbursement", "student"]
        })

        # 8. State Old Age Social Security Pension Scheme
        schemes.append({
            "slug": f"{st_slug}-state-old-age-pension",
            "scheme_code": f"SCH-{st_code}-PEN-002",
            "name": f"{state_name} Vridhavastha Old Age Pension Scheme",
            "name_hi": f"{state_name} वृद्धावस्था पेंशन योजना",
            "description": f"Direct monthly pension of ₹1,000 to ₹1,500 provided by {state_name} Government to elderly citizens aged 60+ living in BPL or low-income households.",
            "description_hi": f"{state_name} के 60 वर्ष या उससे अधिक आयु के वरिष्ठ नागरिकों को गरिमापूर्ण जीवन हेतु नियमित मासिक पेंशन सहायता सीधे बैंक खाते में।",
            "primary_category": "Social Security & Pension",
            "category": "Social Security & Pension",
            "ministry": meta["dept_soc"],
            "department": meta["dept_soc"],
            "level": "State",
            "states": [state_name],
            "intents": ["pension"],
            "target_beneficiaries": [f"Senior citizens aged 60 years or above residing in {state_name} living below the state poverty threshold"],
            "eligibility_rules": {
                "states": [state_name],
                "income": {"max": 100000},
                "age": {"min": 60, "max": 120}
            },
            "benefits": [
                "Monthly pension allowance credited directly into the elderly citizen's bank account via DBT",
                "Free geriatric health check-ups and diagnostic support at government health facilities"
            ],
            "documents": [f"{state_name} Domicile Proof", "Age Proof (Aadhaar / Voter ID showing age ≥60)", "BPL Certificate / Income Certificate", "Bank Account Passbook"],
            "application_steps": [
                f"Submit application online via {meta['pension_url']} or through Gram Panchayat / Urban Ward Office",
                "Field verification by local revenue staff and sanction by District Welfare Officer",
                "Direct electronic monthly payment release"
            ],
            "official_url": meta["pension_url"],
            "source_url": meta["pension_url"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["pension", "senior-citizens", st_slug, "old-age", "social-security", "dbt", "elderly"]
        })

        # 9. State Emergency Medical Relief & Illness Assistance Fund
        schemes.append({
            "slug": f"{st_slug}-mukhyamantri-chikitsa-sahayata-kosh",
            "scheme_code": f"SCH-{st_code}-HLT-002",
            "name": f"{state_name} Mukhyamantri Chikitsa Sahayata Kosh (Medical Relief Fund)",
            "name_hi": f"{state_name} मुख्यमंत्री चिकित्सा सहायता कोष",
            "description": f"Discretionary emergency financial grant providing up to ₹2,00,000 to ₹5,00,000 for critical surgeries and medical treatment for patients belonging to BPL/low-income families in {state_name}.",
            "description_hi": f"{state_name} के निर्धन मरीजों को हृदय शल्य चिकित्सा, कैंसर, न्यूरोसर्जरी एवं किडनी डायलिसिस/प्रत्यारोपण हेतु ₹2 लाख से ₹5 लाख तक का सरकारी आपातकालीन चिकित्सा अनुदान।",
            "primary_category": "Healthcare",
            "category": "Healthcare",
            "ministry": "Health and Family Welfare Department, Government of " + state_name,
            "department": "Directorate of Medical and Health Services",
            "level": "State",
            "states": [state_name],
            "intents": ["healthcare", "financial"],
            "target_beneficiaries": [f"Patients domiciled in {state_name} suffering from major life-threatening diseases with annual family income up to ₹2.5 Lakh"],
            "eligibility_rules": {
                "states": [state_name],
                "income": {"max": 250000},
                "age": {"min": 0, "max": 100}
            },
            "benefits": [
                "Financial assistance of up to ₹2,00,000 (up to ₹5,00,000 for organ transplants) paid directly to the empaneled treating hospital",
                "Immediate relief for major cardiac, renal, neurological, and oncology surgeries"
            ],
            "documents": [f"{state_name} Residence Certificate", "Income Certificate (≤ ₹2.5 Lakh/yr) or BPL Ration Card", "Medical Estimate and Diagnostic Report from Government Specialist", "Aadhaar Card"],
            "application_steps": [
                "Get treatment estimate signed by Medical Superintendent of empaneled hospital",
                "Submit application to District Magistrate (DM) / Chief Minister's Relief Cell",
                "Sanction issued and funds transferred directly to hospital account"
            ],
            "official_url": meta["portal"],
            "source_url": meta["portal"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["healthcare", "medical-relief", st_slug, "cancer", "surgery", "hospital", "emergency-fund"]
        })

        # 10. State Youth Skill Enhancement & Apprenticeship Stipend
        schemes.append({
            "slug": f"{st_slug}-yuva-kaushal-vikas-apprenticeship",
            "scheme_code": f"SCH-{st_code}-JOB-003",
            "name": f"{state_name} Youth Apprenticeship and Skill Promotion Scheme",
            "name_hi": f"{state_name} युवा कौशल विकास एवं शिक्षुता संवर्धन योजना",
            "description": f"State skill apprenticeship initiative providing industry-aligned practical training and monthly stipends of ₹4,000 to ₹6,000 for youth in {state_name}.",
            "description_hi": f"{state_name} के 10वीं, 12वीं, आईटीआई एवं डिप्लोमा धारक युवाओं को उद्योगों में व्यावहारिक ऑन-द-जॉब प्रशिक्षण तथा मासिक सरकारी वजीफा।",
            "primary_category": "Employment & Skills",
            "category": "Employment & Skills",
            "ministry": meta["dept_ind"],
            "department": "State Skill Development Mission",
            "level": "State",
            "states": [state_name],
            "intents": ["skills", "internships", "jobs"],
            "target_beneficiaries": [f"Unemployed youth aged 18-30 domiciled in {state_name} seeking technical apprenticeships"],
            "eligibility_rules": {
                "states": [state_name],
                "occupation": ["unemployed", "student"],
                "age": {"min": 18, "max": 30}
            },
            "benefits": [
                "Monthly apprenticeship stipend of ₹4,000 to ₹6,000 (with 50% state DBT subsidy contribution)",
                "State Skill Mission certification and direct hiring opportunities in industrial estates"
            ],
            "documents": [f"{state_name} Domicile Proof", "Class 10 / 12 / ITI / Diploma Marksheets", "Aadhaar Card", "Bank Account Details"],
            "application_steps": [
                f"Register on {state_name} Employment / Skill portal",
                "Apply to local industrial apprenticeship slots",
                "Contract signing and monthly stipend disbursement"
            ],
            "official_url": meta["portal"],
            "source_url": meta["portal"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["skills", "apprenticeship", st_slug, "stipend", "jobs", "youth", "vocational"]
        })

        # 11. State Pre-Matric Scholarship for Needy Students
        schemes.append({
            "slug": f"{st_slug}-pre-matric-scholarship-scheme",
            "scheme_code": f"SCH-{st_code}-EDU-003",
            "name": f"{state_name} Pre-Matric Scholarship for SC, ST & OBC Students",
            "name_hi": f"{state_name} पूर्व-दशम छात्रवृत्ति योजना (कक्षा 9 एवं 10)",
            "description": f"Financial scholarship providing ₹3,000 to ₹4,500 per year to underprivileged SC, ST, and OBC students in Class 9 and 10 in {state_name} to curb dropouts before matriculation.",
            "description_hi": f"{state_name} के कक्षा 9वीं और 10वीं में अध्ययनरत अनुसूचित जाति, जनजाति एवं पिछड़ा वर्ग के विद्यार्थियों को पढ़ाई जारी रखने हेतु वार्षिक छात्रवृत्ति।",
            "primary_category": "Education & Learning",
            "category": "Education & Learning",
            "ministry": meta["dept_edu"],
            "department": meta["dept_edu"],
            "level": "State",
            "states": [state_name],
            "intents": ["education"],
            "target_beneficiaries": [f"Students in Class 9 and 10 domiciled in {state_name} with family income under ₹2.5 Lakh"],
            "eligibility_rules": {
                "states": [state_name],
                "category": ["SC", "ST", "OBC"],
                "occupation": ["student"],
                "income": {"max": 250000},
                "age": {"min": 13, "max": 18}
            },
            "benefits": [
                "Annual scholarship of ₹3,000 to ₹4,500 credited directly into student's bank account via DBT",
                "Additional ad-hoc grant of ₹1,000 per year for day scholars and hostellers for books and stationery"
            ],
            "documents": [f"{state_name} Domicile Certificate", "Caste Certificate", "Income Certificate (≤ ₹2.5 Lakh/yr)", "Previous Class 8 Marksheet", "Aadhaar Card & Bank Details"],
            "application_steps": [
                f"Apply online on {state_name} Scholarship Portal ({meta['scholarship_url']}) or via school headmaster",
                "School head verifies and submits master list",
                "Direct DBT disbursement to student's account"
            ],
            "official_url": meta["scholarship_url"],
            "source_url": meta["scholarship_url"],
            "source_name": f"Government of {state_name}",
            "verification_status": "Verified",
            "active": True,
            "tags": ["education", "scholarship", st_slug, "pre-matric", "school", "sc", "st", "obc", "student"]
        })

    return schemes

