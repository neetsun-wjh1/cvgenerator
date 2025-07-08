from typing import Dict, Any

SECTION_TEMPLATES: Dict[str, Dict[str, Any]] = {

    "main_particulars": {
            "label": "Main Particulars",
            "type": "TAB",
            "fields": [
                {"name": "Name", "value": "[Profile Official Name]", "type": "TXT"},
                {"name": "Designation", "value": "[Profile Official Designation]", "type": "TXT"},
                {"name": "Country", "value": "[Profile Country of Birth]", "type": "TXT"},
                {"name": "Birth Date", "value": "[Profile Birthdate in DD MM YYYY]", "type": "DTT"},
                {"name": "Marital Status", "value": "[Profile marital status, with details on the number of children if any]", "type": "TXT"}
            ]
        },

    "education": {
        "label": "Education",
        "type": "TAB",
        "fields": [
            {
                "name": "[Qualification Name]",
                "value": "[Institution Name], [Country of Institution] ([Start Month Year - End Month Year of studies])",
                "type": "TXT"
            }
        ]
    },

    "career": {
        "label": "Career",
        "type": "TAB",
        "fields": [
            {
                "name": "[Name of Position]",
                "value": "[Company or Organization Name], [Country of Company/Organization] ([Start Month Year - End Month Year of employment])",
                "type": "TXT"
            }
        ]
    },

    "appointments": {
        "label": "Appointments",
        "type": "TAB",
        "fields": [
            {
                "name": "[Name of Position or Title]",
                "value": "[Company or Organization Name], [Country of Company/Organization] ([Start Month Year - End Month Year of tenure])",
                "type": "TXT"
            }
        ]
    },
    "languages": {
        "label": "Languages",
        "type": "TAB",
        "fields": [
            {
                "name": "[Language Name]",
                "value": "[Proficiency Level (e.g., Fluent, Conversational, Basic)]",
                "type": "TXT"
            }
        ]
    },
    "remarks": {
        "label": "Remarks",
        "type": "TAB",
        "fields": [
            {
                "name": "Remarks",
                "value": "[Any additional noteworthy information or personal achievements, including familial connections to other notable figures if relevant.]",
                "type": "LTX"
            }
        ]
    },

    "reference": {
        "label": "Reference",
        "type": "TAB",
        "fields": [
            {
                "name": "[Link Title]",
                "value": "[URL link]",
                "type": "TXT"
            }
        ]
    }
}

def messagePromptInstruction(sectionName: str) -> str:
    match sectionName:
        case "main_particulars":
            return """"
            For main particulars, provide comprehensive personal details including:
            - Full legal name (including middle names if available)
            - Current professional designation/title
            - Country of residence or primary nationality
            - Birth date in DD MMM YYYY format (e.g., "14 Jun 1946")
            - Marital status with family details (number of marriages, children count and gender breakdown)

            """
        case "education":
            return """"
            For the education section, provide detailed academic background including:
                - Educational institutions attended (universities, colleges, schools, academies)
                - Degree types and fields of study (Bachelor's, Master's, PhD, certificates, diplomas)
                - Locations of institutions (city, state/province, country)
                - Duration of studies (start and end dates or years attended)
             Education entries can include Professional certifications, specialized training programs, Military academy and specialized institutional training
            
                Ensure each entry includes:
                1. Institution name as the field "name"
                2. Complete details (degree/program, institution, location, duration) as the "value"
                3. "type" set to "TXT"

            Return 10 and more entries.
            """

        case "career":
            return """
            For the CAREER SECTION, provide professional career positions including:
                - Governmental positions (President, Governor, Senator, etc.)
                - Corporate positions

            Ensure each entry includes:
            1. Position/Role/Source name as the field "name"
            2. Complete details (organization, location, duration)
            3. "type" set to "TXT" for all fields

            Return 10 and more entries.
            """

        case "reference":
            return """
            Include the hyperlink source for all the retrieved information in reference section.

            Ensure each entry includes:
            1. Website Page Name as the field "name"
            2. hyperlink within the field "value"
            3. "type" set to "TXT" for all fields
            """

        case "appointments":
            return """
            Provide business appointments, entrepreneurial ventures, and other professional roles including all professional appointments outside of primary career track

            Ensure each entry includes:
            1. Position/Role/Source name as the field "name"
            2. Complete details (organization, location, duration)
            3. "type" set to "TXT" for all fields

            Return 5 and more entries.
            """
        case "languages":
            return """
            For the languages section, provide details of languages spoken including:
                - Language names
                - Proficiency levels (Fluent, Conversational, Basic, etc.)

            Ensure each entry includes:
            1. Language name as the field "name"
            2. Proficiency level as the field "value"
            3. "type" set to "TXT" for all fields
            
            """
        
        case _:  # default case (optional)
            return """"none"""