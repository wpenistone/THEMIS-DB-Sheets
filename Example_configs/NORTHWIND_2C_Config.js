const THEMIS_CONFIG = {
    "DATE_FORMAT": "MM/DD/YY",
    "LAYOUT_BLUEPRINTS": {
        "BILLET_OFFSETS": {
            "offsets": {
                "username": { "row": 0, "col": 0 },
                "region": { "row": 1, "col": -1 },
                "joinDate": { "row": 1, "col": 0 },
                "discordId": { "row": 1, "col": 1 },
                "LOAcheckbox": { "row": 1, "col": 2 }
            }
        },
        "SQUAD_OFFSETS_ENLISTED": {
            "offsets": {
                "rank": { "row": 0, "col": 0 },
                "username": { "row": 0, "col": 1 },
                "discordId": { "row": 0, "col": 4 },
                "region": { "row": 0, "col": 5 },
                "joinDate": { "row": 0, "col": 6 },
                "LOAcheckbox": { "row": 0, "col": 7 },
                "BTcheckbox": { "row": 0, "col": 8 }
            }
        },
        "SQUAD_OFFSETS_NCO": {
            "offsets": {
                "rank": { "row": 0, "col": 0 },
                "username": { "row": 0, "col": 1 },
                "discordId": { "row": 0, "col": 4 },
                "region": { "row": 0, "col": 5 },
                "joinDate": { "row": 0, "col": 6 },
                "LOAcheckbox": { "row": 0, "col": 7 }
            }
        }
    },
    "SLOT_BLUEPRINTS": {
        "STANDARD_SQUAD": [
            { "rank": "Staff Sergeant", "location": { "rows": [9] }, "layout": "SQUAD_OFFSETS_NCO" },
            { "rank": "Colour Sergeant", "location": { "rows": [10] }, "layout": "SQUAD_OFFSETS_NCO" },
            { "rank": "Sergeant", "count": 2, "location": { "rows": [12, 13] }, "layout": "SQUAD_OFFSETS_NCO" },
            { "rank": "Corporal", "count": 3, "location": { "rows": [15, 16, 17] }, "layout": "SQUAD_OFFSETS_NCO" },
            
            {
                "ranks": ["Private", "Private First Class", "Lance Corporal"],
                "count": 21,
                "location": { "startRow": 19, "endRow": 39 },
                "layout": "SQUAD_OFFSETS_ENLISTED" 
            }
        ]
    },
    "ORGANIZATION_HIERARCHY": [
        {
            "children": [
                {
                    "children": [
                        { "location": { "startCol": 6 }, "name": "First Alpha", "shortcuts": ["1A"], "useSlotsFrom": "STANDARD_SQUAD" },
                        { "location": { "startCol": 18 }, "name": "First Bravo", "shortcuts": ["1B"], "useSlotsFrom": "STANDARD_SQUAD" }
                    ],
                    "name": "First Platoon", "shortcuts": ["1P"], "sheetName": "First Platoon",
                    "eventLogStart": { "row": 6, "col": 4 },
                    "logShortSectionName": true,
                    "slots": [
                        { "layout": "BILLET_OFFSETS", "location": { "col": 7, "row": 22, "sheetName": "Headquarters" }, "rank": "Lieutenant", "title": "Lieutenant" },
                        { "layout": "BILLET_OFFSETS", "location": { "col": 7, "row": 26, "sheetName": "Headquarters" }, "rank": "Ensign", "title": "Ensign" },
                        { "layout": "BILLET_OFFSETS", "location": { "col": 7, "row": 30, "sheetName": "Headquarters" }, "rank": "Warrant Officer", "title": "Warrant Officer" }
                    ]
                },
                {
                    "children": [
                        { "location": { "startCol": 6 }, "name": "Second Alpha", "shortcuts": ["2A"], "useSlotsFrom": "STANDARD_SQUAD" },
                        { "location": { "startCol": 18 }, "name": "Second Bravo", "shortcuts": ["2B"], "useSlotsFrom": "STANDARD_SQUAD" }
                    ],
                    "name": "Second Platoon", "shortcuts": ["2P"], "sheetName": "Second Platoon",
                    "eventLogStart": { "row": 6, "col": 11 },
                    "logShortSectionName": true,
                    "slots": [
                        { "layout": "BILLET_OFFSETS", "location": { "col": 16, "row": 22, "sheetName": "Headquarters" }, "rank": "Lieutenant", "title": "Lieutenant" },
                        { "layout": "BILLET_OFFSETS", "location": { "col": 16, "row": 26, "sheetName": "Headquarters" }, "rank": "Ensign", "title": "Ensign" },
                        { "layout": "BILLET_OFFSETS", "location": { "col": 16, "row": 30, "sheetName": "Headquarters" }, "rank": "Warrant Officer", "title": "Warrant Officer" }
                    ]
                }
            ],
            "name": "Company Headquarters", "sheetName": "Headquarters",
            "eventLogStart": { "row": 6, "col": 25 },
            "eventLogColumns": {
                "DAY": 0,
                "HOST": 1,
                "TYPE": 2
            },
            "slots": [
                { "layout": "BILLET_OFFSETS", "location": { "col": 16, "row": 7 }, "rank": "Major", "title": "Major" },
                { "layout": "BILLET_OFFSETS", "location": { "col": 16, "row": 11 }, "rank": "Captain", "title": "Captain" },
                { "layout": "BILLET_OFFSETS", "location": { "col": 16, "row": 15 }, "rank": "Company Colour Sergeant", "title": "Company Colour Sergeant" }
            ]
        }
    ],
    "REGIONS": ["NA", "SA", "EU", "AS", "OC"],
    "RANK_HIERARCHY": [
        { "abbr": "PVT", "name": "Private" }, { "abbr": "PFC", "name": "Private First Class" }, { "abbr": "LCPL", "name": "Lance Corporal" },
        { "abbr": "CPL", "name": "Corporal" }, { "abbr": "SGT", "name": "Sergeant" }, { "abbr": "CSGT", "name": "Colour Sergeant" },
        { "abbr": "SSGT", "name": "Staff Sergeant" }, { "abbr": "WO", "name": "Warrant Officer" }, { "abbr": "ENS", "name": "Ensign" },
        { "abbr": "LT", "name": "Lieutenant" }, { "abbr": "CCS", "name": "Company Colour Sergeant" }, { "abbr": "CPT", "name": "Captain" }, { "abbr": "MJR", "name": "Major" }
    ],
    "RECRUITER_MIN_RANK": "Staff Sergeant",
    "RECRUITMENT_LOG_SHEET_NAME": "Recruitment Logbook",
    "RECRUITMENT_LOG_START_ROW": 4, 
    "RECRUITMENT_LOG_END_ROW": 78,
    "RECRUITMENT_LOG_COLUMNS": { "DATE": 3, "USERNAME": 4, "DISCORD_ID": 5, "REGION": 6, "SQUAD": 7, "RECRUITER": 8 },    "EVENT_LOG_SHEET_NAME": "Event Logbook",
    "EVENT_LOG_COLUMNS": { "SECTION": 0, "DAY": 1, "HOST": 2, "TYPE": 3 },
    "ATTENDANCE_SHEET_NAME": "Attendance Logbook",
    "ATTENDANCE_DATA_START_ROW": 5,
    "ATTENDANCE_DATA_END_ROW": 147,
    "ATTENDANCE_DAY_COLUMNS": { "Monday": 3, "Tuesday": 5, "Wednesday": 7, "Thursday": 9, "Friday": 11, "Saturday": 13, "Sunday": 15 },
    "EVENT_TYPE_DEFINITIONS": [
        { "name": "Combat Training", "aliases": ["CT"] }, { "name": "Crate Run", "aliases": ["Crates"] }, { "name": "Rally", "aliases": ["Drill"] },
        { "name": "Raid", "aliases": [] }, { "name": "Patrol", "aliases": ["Recon"] }, { "name": "Fort Event", "aliases": [] },
        { "name": "Miscellaneous Event", "aliases": ["Misc Event"] }, { "name": "Mandatory Event", "aliases": ["MA"] }, { "name": "Practise Raid", "aliases": ["PR", "Practice Raid"] }
    ],
    "TIME_IN_RANK_REQUIREMENTS": { "COMPANY COLOUR SERGEANT": 30, "COLOUR SERGEANT": 7, "STAFF SERGEANT": 14, "WARRANT OFFICER": 18, "ENSIGN": 24, "LIEUTENANT": 38 },
    "WEBHOOK_URL": "",
    "THEMIS_CLIENT_API_KEY": "",
    "LOA_MENTION_ROLE_ID": "your_role_id",
    "LOCK_TIMEOUT_MS": 15000,
    "CACHE_KEYS": { "COMPANY": "global_companymen_cache_v9", "RECRUIT_DATA": "recruit_data_cache_v9", "SHEET_DATA_PREFIX": "sheet_data_v2_", "USER_DATA_PREFIX": "user_data_", "TOTAL_SLOTS_MAP": "total_slots_map_cache_v2", "WEBHOOK_QUEUE_KEY": "webhook_queue_v1" },
    "CACHE_DURATIONS": { "LONG": 21600, "STANDARD": 3600, "SHORT": 1800 },
    "UBT_SETTINGS": { "NAME": "UBT", "PROMPT_MESSAGE": "This promotion requires the member to be {name} passed. Is this correct?", "TRIGGER_RANK": "Private First Class" },
    "LOGIC_THRESHOLDS": {
        "EMAIL_REQUIRED_MIN_RANK": { "CONDITION": ">=Staff Sergeant", "PROMPT": "Promotions to this rank or higher require an email on file. Please provide one for this member." },
        "MIN_HOST_RANK": "Corporal"
    },
    "VALIDATION_RULES": {
        "USERNAME": { "REGEX": "^[a-zA-Z0-9_]+$", "REGEX_ERROR": "Invalid characters used.", "MIN_LENGTH": 3, "MAX_LENGTH": 20, "LENGTH_ERROR": "Must be 3-20 characters.", "NO_START_END_UNDERSCORE": true, "START_END_UNDERSCORE_ERROR": "Cannot start or end with an underscore.", "MAX_UNDERSCORES": 1, "MAX_UNDERSCORES_ERROR": "Only one underscore is allowed." }
    },
    "SHEET_ACCESS_MANAGEMENT": { "ON_RECRUIT": "ALWAYS", "ON_DELETE": "ALWAYS" },
    "CUSTOM_FIELDS": [],
    "CUSTOM_FIELDS_UI_EDITABLE": false
};