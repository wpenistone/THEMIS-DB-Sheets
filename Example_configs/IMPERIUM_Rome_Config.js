const THEMIS_CONFIG = {
    "DATE_FORMAT": "MM/DD/YY",
    "EVENT_LOG_SHEET_NAME": "Event Logbook",
    "EVENT_LOG_COLUMNS": {
      "SECTION": 0,
      "DAY": 1,
      "HOST": 2,
      "TYPE": 3
    },
    "ATTENDANCE_SHEET_NAME": "Attendance Logbook",
    "ATTENDANCE_DATA_START_ROW": 5,
    "ATTENDANCE_DATA_END_ROW": 147,
    "ATTENDANCE_DAY_COLUMNS": {
      "Monday": 3,
      "Tuesday": 5,
      "Wednesday": 7,
      "Thursday": 9,
      "Friday": 11,
      "Saturday": 13,
      "Sunday": 15
    },

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
       
        "BILLET_NCO_OFFSETS": {
          "offsets": {
            "rank": { "row": 0, "col": 0 },
            "username": { "row": 0, "col": 1 },
            "discordId": { "row": 0, "col": 4 },
            "region": { "row": 0, "col": 5 },
            "joinDate": { "row": 0, "col": 6 },
            "LOAcheckbox": { "row": 0, "col": 7 }
          }
        },
        "SQUAD_OFFSETS": { 
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
        "SERVIUS_OFFSETS": {
          "offsets": {
            "rank": { "row": 0, "col": 0 },
            "username": { "row": 0, "col": 1 },
            "phase": { "row": 0, "col": 4 },
            "discordId": { "row": 0, "col": 5 },
            "region": { "row": 0, "col": 6 },
            "joinDate": { "row": 0, "col": 7 },
            "LOAcheckbox": { "row": 0, "col": 8 },
            "BTcheckbox": { "row": 0, "col": 9 }
          }
        }
      },
        "SLOT_BLUEPRINTS": {
          "STANDARD_CONTUBERNIUM": [{
              "layout": "BILLET_NCO_OFFSETS",
              "rank": "Decanus",
              "count": 1,
              "location": {
                "row": 12
              } 
            },
            {
              "ranks": ["Tirones", "Auxilia", "Milites", "Immunes"],
              "count": 23,
              "location": { "startRow": 17, "endRow": 39 }
            }
          ],
          "CONTUBERNIUM_LOW": [{
              "layout": "BILLET_NCO_OFFSETS", 
              "rank": "Decanus",
              "location": { "row": 44 }
            },
            {
              "layout": "BILLET_NCO_OFFSETS", 
              "rank": "Cornicen",
              "location": { "startRow": 46, "endRow": 47 },
              "count": 2
            },
            {
              "ranks": ["Tirones", "Auxilia", "Milites", "Immunes"],
              "count": 23,
              "location": { "startRow": 49, "endRow": 71 }
            }
          ],
          "OLYMPUS_CONTUBERNIUM": [{
              "layout": "BILLET_NCO_OFFSETS", 
              "rank": "Decanus",
              "location": { "row": 12 }
            },
            {
              "layout": "BILLET_NCO_OFFSETS", 
              "rank": "Cornicen",
              "location": { "startRow": 14, "endRow": 15 },
              "count": 2
            },
            {
              "ranks": ["Immunes", "Milites"],
              "count": 13,
              "location": { "startRow": 17, "endRow": 29 }
            }
          ],
          "AUGUSTII_CONTUBERNIUM": [{
              "layout": "BILLET_NCO_OFFSETS", 
              "rank": "Decanus",
              "location": { "row": 34 }
            },
            {
              "layout": "BILLET_NCO_OFFSETS", 
              "rank": "Cornicen",
              "location": { "startRow": 36, "endRow": 37 },
              "count": 2
            },
            {
              "ranks": ["Immunes", "Milites"],
              "count": 7,
              "location": { "startRow": 39, "endRow": 45 }
            }
          ],
          "SERVIUS_CONTUBERNIUM": [{
              "ranks": ["Tirones"],
              "count": 21,
              "location": { "startRow": 5, "endRow": 25 }
            }
          ]
        },
    "ORGANIZATION_HIERARCHY": [{
      "children": [{
        "name": "Legio VI",
        "sheetName": "Legio VI",
        "layout": "BILLET_OFFSETS",
        "slots": [
          {
            "rank": "Legatus",
            "layout": "BILLET_OFFSETS",
            "location": { "row": 6, "col": 16 }
          }, {
            "rank": "Tribunus",
            "title": "First Cohort Tribunus",
            "layout": "BILLET_OFFSETS",
            "location": { "row": 10, "col": 7 }
          }, {
            "rank": "Tribunus",
            "title": "Second Cohort Tribunus",
            "layout": "BILLET_OFFSETS",
            "location": { "row": 10, "col": 25 }
          }
        ],
        "children": [{
          "name": "First Cohort",
          "sheetName": "VI First Cohort",
          "slots": [{
            "rank": "Praefectus", "layout": "BILLET_OFFSETS",
            "location": { "row": 6, "col": 16 }
          },
          {
            "rank": "Primus Pilus", "layout": "BILLET_OFFSETS",
            "location": { "row": 10, "col": 16 }
          },
          {
            "rank": "Aquilifer", "layout": "BILLET_OFFSETS",
            "location": { "row": 14, "col": 16 }
          }],
          "children": [{
            "name": "First Century", "sheetName": "VI I.C. 1C",
            "slots": [
              { "rank": "Centurion", "layout": "BILLET_OFFSETS", "location": { "row": 21, "col": 7, "sheetName": "VI First Cohort" } },
              { "rank": "Optio", "layout": "BILLET_OFFSETS", "location": { "row": 25, "col": 7, "sheetName": "VI First Cohort" } },
              { "rank": "Signifer", "layout": "BILLET_OFFSETS", "location": { "row": 29, "col": 7, "sheetName": "VI First Cohort" } },
              { "rank": "Tesserarius", "title": "First Aquilia & Bellum Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 4 } },
              { "rank": "Tesserarius", "title": "First Caesar & Dominus Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 16 } }
            ],
            "children": [
              { "name": "Aquilia Contubernium", "shortcuts": ["VI 1A"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "STANDARD_CONTUBERNIUM" },
              { "name": "Bellum Contubernium", "shortcuts": ["VI 1B"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "CONTUBERNIUM_LOW" },
              { "name": "Caesar Contubernium", "shortcuts": ["VI 1C"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 16 }, "useSlotsFrom": "STANDARD_CONTUBERNIUM" },
              { "name": "Dominus Contubernium", "shortcuts": ["VI 1D"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 16 }, "useSlotsFrom": "CONTUBERNIUM_LOW" }
            ]
          },
          {
            "name": "Second Century", "sheetName": "VI I.C. 2C",
            "slots": [
              { "rank": "Centurion", "layout": "BILLET_OFFSETS", "location": { "row": 21, "col": 25, "sheetName": "VI First Cohort" } },
              { "rank": "Optio", "layout": "BILLET_OFFSETS", "location": { "row": 25, "col": 25, "sheetName": "VI First Cohort" } },
              { "rank": "Signifer", "layout": "BILLET_OFFSETS", "location": { "row": 29, "col": 25, "sheetName": "VI First Cohort" } },
              { "rank": "Tesserarius", "title": "Second Aquilia & Bellum Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 4 } },
              { "rank": "Tesserarius", "title": "Second Caesar & Dominus Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 16 } }
            ],
            "children": [
              { "name": "Aquilia Contubernium", "shortcuts": ["VI 2A"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "STANDARD_CONTUBERNIUM" },
              { "name": "Bellum Contubernium", "shortcuts": ["VI 2B"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "CONTUBERNIUM_LOW" },
              { "name": "Caesar Contubernium", "shortcuts": ["VI 2C"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 16 }, "useSlotsFrom": "STANDARD_CONTUBERNIUM" },
              { "name": "Dominus Contubernium", "shortcuts": ["VI 2D"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 16 }, "useSlotsFrom": "CONTUBERNIUM_LOW" }
            ]
          },
          {
            "name": "Praetorian Century", "sheetName": "VI I.C. PC",
            "slots": [
              { "rank": "Centurion", "layout": "BILLET_OFFSETS", "location": { "row": 21, "col": 16, "sheetName": "VI First Cohort" } },
              { "rank": "Optio", "layout": "BILLET_OFFSETS", "location": { "row": 25, "col": 16, "sheetName": "VI First Cohort" } },
              { "rank": "Signifer", "layout": "BILLET_OFFSETS", "location": { "row": 29, "col": 16, "sheetName": "VI First Cohort" } },
              { "rank": "Tesserarius", "title": "Praetorian Olympus Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 4 } },
              { "rank": "Tesserarius", "title": "Praetorian Cerberus Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 16 } }
            ],
            "children": [
              { "name": "Servius Auxiliary", "shortcuts": ["VI S"], "sheetName": "VI I.C. PC S", "layout": "SERVIUS_OFFSETS", "location": { "startCol": 3 }, "useSlotsFrom": "SERVIUS_CONTUBERNIUM" },
              { "name": "Olympus", "shortcuts": ["VI O"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "OLYMPUS_CONTUBERNIUM" },
              { "name": "Cerberus", "shortcuts": ["VI CB"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 16 }, "useSlotsFrom": "OLYMPUS_CONTUBERNIUM" },
              { "name": "Augustii Evocatii", "shortcuts": ["VI AU"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "AUGUSTII_CONTUBERNIUM" }
            ]
          }]
        },
        {
          "name": "Second Cohort", "sheetName": "VI Second Cohort",
          "slots": [
            { "rank": "Praefectus", "layout": "BILLET_OFFSETS", "location": { "row": 6, "col": 16 } },
            { "rank": "Primus Pilus", "layout": "BILLET_OFFSETS", "location": { "row": 10, "col": 16 } },
            { "rank": "Aquilifer", "layout": "BILLET_OFFSETS", "location": { "row": 14, "col": 16 } }
          ],
          "children": [{
            "name": "Third Century", "sheetName": "VI II.C. 3C",
            "slots": [
              { "rank": "Centurion", "layout": "BILLET_OFFSETS", "location": { "row": 21, "col": 7, "sheetName": "VI Second Cohort" } },
              { "rank": "Optio", "layout": "BILLET_OFFSETS", "location": { "row": 25, "col": 7, "sheetName": "VI Second Cohort" } },
              { "rank": "Signifer", "layout": "BILLET_OFFSETS", "location": { "row": 29, "col": 7, "sheetName": "VI Second Cohort" } },
              { "rank": "Tesserarius", "title": "Third Aquilia & Bellum Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 4 } },
              { "rank": "Tesserarius", "title": "Third Caesar & Dominus Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 16 } }
            ],
            "children": [
              { "name": "Aquilia Contubernium", "shortcuts": ["VI 3A"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "STANDARD_CONTUBERNIUM" },
              { "name": "Bellum Contubernium", "shortcuts": ["VI 3B"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "CONTUBERNIUM_LOW" },
              { "name": "Caesar Contubernium", "shortcuts": ["VI 3C"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 16 }, "useSlotsFrom": "STANDARD_CONTUBERNIUM" },
              { "name": "Dominus Contubernium", "shortcuts": ["VI 3D"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 16 }, "useSlotsFrom": "CONTUBERNIUM_LOW" }
            ]
          },
          {
            "name": "Fourth Century", "sheetName": "VI II.C. 4C",
            "slots": [
              { "rank": "Centurion", "layout": "BILLET_OFFSETS", "location": { "row": 21, "col": 25, "sheetName": "VI Second Cohort" } },
              { "rank": "Optio", "layout": "BILLET_OFFSETS", "location": { "row": 25, "col": 25, "sheetName": "VI Second Cohort" } },
              { "rank": "Signifer", "layout": "BILLET_OFFSETS", "location": { "row": 29, "col": 25, "sheetName": "VI Second Cohort" } },
              { "rank": "Tesserarius", "title": "Fourth Aquilia & Bellum Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 4 } },
              { "rank": "Tesserarius", "title": "Fourth Caesar & Dominus Tesserarius", "layout": "BILLET_NCO_OFFSETS", "location": { "row": 7, "col": 16 } }
            ],
            "children": [
              { "name": "Aquilia Contubernium", "shortcuts": ["VI 4A"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "STANDARD_CONTUBERNIUM" },
              { "name": "Bellum Contubernium", "shortcuts": ["VI 4B"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 4 }, "useSlotsFrom": "CONTUBERNIUM_LOW" },
              { "name": "Caesar Contubernium", "shortcuts": ["VI 4C"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 16 }, "useSlotsFrom": "STANDARD_CONTUBERNIUM" },
              { "name": "Dominus Contubernium", "shortcuts": ["VI 4D"], "layout": "SQUAD_OFFSETS", "location": { "startCol": 16 }, "useSlotsFrom": "CONTUBERNIUM_LOW" }
            ]
          }]
        }]
      }]
    ,
      "layout": "BILLET_OFFSETS",
      "name": "Rome HQ",
      "eventLogStart": {
        "row": 4,
        "col": 3  
      },
      "sheetName": "Rome HQ",
      "slots": [{
        "count": 2,
        "layout": "BILLET_OFFSETS",
        "locations": [{
          "col": 7,
          "row": 6
        },
        {
          "col": 17,
          "row": 6
        }],
        "rank": "Consul"
      },
      {
        "count": 5,
        "layout": "BILLET_OFFSETS",
        "locations": [{
          "col": 7,
          "row": 10
        },
        {
          "col": 17,
          "row": 10
        },
        {
          "col": 7,
          "row": 14
        },
        {
          "col": 17,
          "row": 14
        },
        {
          "col": 7,
          "row": 18
        }
        ],
        "rank": "Praetor"},
      {
        "count": 1,
        "layout": "BILLET_OFFSETS",
        "locations": [
        {
          "col": 17,
          "row": 18
        }],
        "rank": "Praefectus"
      }]
    }],
    "REGIONS": ["NA", "SA", "EU", "AS", "OC"],
    "RANK_HIERARCHY": [{
      "abbr": "AUX",
      "name": "Auxilia"
    },
    {
      "abbr": "TIR",
      "name": "Tirones"
    },
    {
      "abbr": "MIL",
      "name": "Milites"
    },
    {
      "abbr": "IMM",
      "name": "Immunes"
    },
    {
      "abbr": "COR",
      "name": "Cornicen"
    },
    {
      "abbr": "DEC",
      "name": "Decanus"
    },
    {
      "abbr": "TES",
      "name": "Tesserarius"
    },
    {
      "abbr": "SIG",
      "name": "Signifer"
    },
    {
      "abbr": "OPT",
      "name": "Optio"
    },
    {
      "abbr": "CEN",
      "name": "Centurion"
    },
    {
      "abbr": "AQF",
      "name": "Aquilifer"
    },
    {
      "abbr": "PIL",
      "name": "Primus Pilus"
    },
    {
      "abbr": "PRF",
      "name": "Praefectus"
    },
    {
      "abbr": "TRI",
      "name": "Tribunus"
    },
    {
      "abbr": "LEG",
      "name": "Legatus"
    },
    {
      "abbr": "PRT",
      "name": "Praetor"
    },
    {
      "abbr": "CON",
      "name": "Consul"
    }],
    "RANKER_RANKS": ["Tirones", "Auxilia", "Milites", "Immunes"],
    "RECRUITER_MIN_RANK": "Tesserarius",
    "RECRUITMENT_LOG_SHEET_NAME": "Recruitment Logbook",
    "RECRUITMENT_LOG_START_ROW": 4, 
    "RECRUITMENT_LOG_END_ROW": 122,
    "RECRUITMENT_LOG_COLUMNS": { "DATE": 3, "USERNAME": 4, "DISCORD_ID": 5, "REGION": 6, "SQUAD": 7, "RECRUITER": 8 },
    "EVENT_TYPE_DEFINITIONS": [{
      "name": "Combat Training",
      "aliases": ["CT", "Combat Practice", "Shooting Drills"]
    },
    {
      "name": "Crate Run",
      "aliases": ["Crates", "Supply Run", "Logistics"]
    },
    {
      "name": "Rally",
      "aliases": ["Drill"]
    },
    {
      "name": "Raid",
      "aliases": ["Fort Raid", "Attack", "Assault"]
    },
    {
      "name": "Patrol",
      "aliases": ["Border Patrol", "Reconnaissance", "Recon"]
    },
    {
      "name": "Fort Event",
      "aliases": ["Fort Defense", "Garrison Duty", "Fort Battle"]
    },
    {
      "name": "Miscellaneous Event",
      "aliases": ["Misc Event", "Other", "Game night", "General Activity"]
    },
    {
      "name": "Roman Basic Training",
      "aliases": ["RBT", "Basic Training"]
    },
    {
      "name": "Mandatory Event",
      "aliases": ["MA", "Mandatory", "Required Attendance"]
    },
    {
      "name": "Phase 1",
      "minAttendees": 1,
      "aliases": ["P1"] 
    }, 
    {
      "name": "Phase 2",
      "minAttendees": 1,
      "aliases": ["P2"]
    }, 
    {
      "name": "Phase 3",
      "minAttendees": 1,
      "aliases": ["P3"]
    }, 
    {
      "name": "Practise Raid",
      "aliases": ["PR", "Mock Raid", "Training Assault", "Practice Raid"]
    }],
    
    "TIME_IN_RANK_REQUIREMENTS": {},
    "WEBHOOK_URL": "",
    "THEMIS_CLIENT_API_KEY": "",
    "LOA_MENTION_ROLE_ID": "your_role_id",
    "LOCK_TIMEOUT_MS": 15000,
    "CACHE_KEYS": {
      "COMPANY": "global_companymen_cache_v9",
      "RECRUIT_DATA": "recruit_data_cache_v9",
      "SHEET_DATA_PREFIX": "sheet_data_v2_",
      "USER_DATA_PREFIX": "user_data_",
      "TOTAL_SLOTS_MAP": "total_slots_map_cache_v2",
      "WEBHOOK_QUEUE_KEY": "webhook_queue_v1"
    },
    "CACHE_DURATIONS": {
      "LONG": 21600,
      "STANDARD": 3600,
      "SHORT": 1800
    },
    "UBT_SETTINGS": {
      "NAME": "RBT",
      "PROMPT_MESSAGE": "This promotion requires the member to be {name} passed. Is this correct?",
      "TRIGGER_RANK": "Milites"
    },
    "VALIDATION_RULES": {
      "USERNAME": {
        "REGEX": "^[a-zA-Z0-9_]+$",
        "REGEX_ERROR": "Invalid characters used.",
        "MIN_LENGTH": 3,
        "MAX_LENGTH": 20,
        "LENGTH_ERROR": "Must be 3-20 characters.",
        "NO_START_END_UNDERSCORE": true,
        "START_END_UNDERSCORE_ERROR": "Cannot start or end with an underscore.",
        "MAX_UNDERSCORES": 1,
        "MAX_UNDERSCORES_ERROR": "Only one underscore is allowed."
      }
    },
    "LOGIC_THRESHOLDS": {
      "EMAIL_REQUIRED_MIN_RANK": {
        "CONDITION": ">=Signifer",
        "PROMPT": "An email is required for this rank. Please provide one."
      },
      "MIN_HOST_RANK": "Cornicen"
    },
    "SHEET_ACCESS_MANAGEMENT": {
      "ON_RECRUIT": "ALWAYS",
      "ON_DELETE": "ALWAYS"
    },
    "CUSTOM_FIELDS": [{
      "key": "phase",
      "label": "Phase",
      "offsetKey": "phase",
      "defaultValue": 1,
      "type": "integer",
      "validation": {
    
        "min": 1,
        "max": 3
      }
    }],
    "CUSTOM_FIELDS_UI_EDITABLE": false
  }