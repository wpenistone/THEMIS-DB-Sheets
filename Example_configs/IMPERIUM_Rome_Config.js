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
        }
      },
        "SLOT_BLUEPRINTS": {
          "STANDARD_CONTUBERNIUM": [{
              "layout": "BILLET_NCO_OFFSETS", 
              "rank": "Decanus",
              "count": 1,
              "location": { "rows": [12] }
            },
            {
              "layout": "BILLET_NCO_OFFSETS", 
              "rank": "Cornicen",
              "location": { "startRow": 14, "endRow": 15 },
              "count": 2
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
              "location": { "rows": [44] }
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
                    ]
          
        },
    "ORGANIZATION_HIERARCHY": [{
      "children": [{
        "children": [{
          "children": [{
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "First Aquilia Contubernium",
            "shortcuts": ["VI 1A"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "First Bellum Contubernium",
            "shortcuts": ["VI 1B"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "First Caesar Contubernium",
            "shortcuts": ["VI 1C"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "First Dominus Contubernium",
            "shortcuts": ["VI 1D"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          }],
          "name": "First Cohort",
          "sheetName": "VI 1C",
          "slots": [{
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 7,
              "row": 25,
              "sheetName": "Legio VI"
            },
            "rank": "Centurion",
            "title": "First Centurion"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 7,
              "row": 29,
              "sheetName": "Legio VI"
            },
            "rank": "Optio",
            "title": "First Optio"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 7,
              "row": 33,
              "sheetName": "Legio VI"
            },
            "rank": "Signifer",
            "title": "First Signifer"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 4,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "First Aquilia & Bellum Tesserarius"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 16,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "First Caesar & Dominus Tesserarius"
          }]
        },
        {
          "children": [{
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "Second Aquilia Contubernium",
            "shortcuts": ["VI 2A"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "Second Bellum Contubernium",
            "shortcuts": ["VI 2B"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "Second Caesar Contubernium",
            "shortcuts": ["VI 2C"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "Second Dominus Contubernium",
            "shortcuts": ["VI 2D"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          }],
          "name": "Second Cohort",
          "sheetName": "VI 2C",
          "slots": [{
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 16,
              "row": 25,
              "sheetName": "Legio VI"
            },
            "rank": "Centurion",
            "title": "Second Centurion"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 16,
              "row": 29,
              "sheetName": "Legio VI"
            },
            "rank": "Optio",
            "title": "Second Optio"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 16,
              "row": 33,
              "sheetName": "Legio VI"
            },
            "rank": "Signifer",
            "title": "Second Signifer"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 4,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "Second Aquilia & Bellum Tesserarius"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 16,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "Second Caesar & Dominus Tesserarius"
          }]
        },
        {
          "children": [{
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "Third Aquilia Contubernium",
            "shortcuts": ["VI 3A"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "Third Bellum Contubernium",
            "shortcuts": ["VI 3B"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "Third Caesar Contubernium",
            "shortcuts": ["VI 3C"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "Third Dominus Contubernium",
            "shortcuts": ["VI 3D"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          }],
          "name": "Third Cohort",
          "sheetName": "VI 3C",
          "slots": [{
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 25,
              "row": 25,
              "sheetName": "Legio VI"
            },
            "rank": "Centurion",
            "title": "Third Centurion"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 25,
              "row": 29,
              "sheetName": "Legio VI"
            },
            "rank": "Optio",
            "title": "Third Optio"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 25,
              "row": 33,
              "sheetName": "Legio VI"
            },
            "rank": "Signifer",
            "title": "Third Signifer"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 4,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "Third Aquilia & Bellum Tesserarius"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 16,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "Third Caesar & Dominus Tesserarius"
          }]
        }],
        "layout": "BILLET_OFFSETS",
        "name": "Legio VI",
        "sheetName": "Legio VI",
        "slots": [{
          "layout": "BILLET_OFFSETS",
          "location": {
            "col": 16,
            "row": 6
          },
          "rank": "Legatus",
          "title": "Legatus"
        },
        {
          "count": 2,
          "layout": "BILLET_OFFSETS",
          "locations": [{
            "col": 7,
            "row": 10
          },
          {
            "col": 25,
            "row": 10
          }],
          "rank": "Tribunus",
          "title": "Tribunus"
        },
        {
          "layout": "BILLET_OFFSETS",
          "location": {
            "col": 16,
            "row": 14
          },
          "rank": "Primus Pilus",
          "title": "Primus Pilus"
        },
        {
          "layout": "BILLET_OFFSETS",
          "location": {
            "col": 16,
            "row": 18
          },
          "rank": "Aquilifer",
          "title": "Aquilifer"
        }]
      },

      {
        "children": [{
          "children": [{
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "First Aquilia Contubernium",
            "shortcuts": ["XIII 1A"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "First Bellum Contubernium",
            "shortcuts": ["XIII 1B"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "First Caesar Contubernium",
            "shortcuts": ["XIII 1C"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "First Dominus Contubernium",
            "shortcuts": ["XIII 1D"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          }],
          "name": "First Cohort",
          "sheetName": "XIII 1C",
          "slots": [{
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 7,
              "row": 25,
              "sheetName": "Legio XIII"
            },
            "rank": "Centurion",
            "title": "First Centurion"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 7,
              "row": 29,
              "sheetName": "Legio XIII"
            },
            "rank": "Optio",
            "title": "First Optio"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 7,
              "row": 33,
              "sheetName": "Legio XIII"
            },
            "rank": "Signifer",
            "title": "First Signifer"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 4,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "First Aquilia & Bellum Tesserarius"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 16,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "First Caesar & Dominus Tesserarius"
          }]
        },
        {
          "children": [{
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "Second Aquilia Contubernium",
            "shortcuts": ["XIII 2A"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "Second Bellum Contubernium",
            "shortcuts": ["XIII 2B"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "Second Caesar Contubernium",
            "shortcuts": ["XIII 2C"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "Second Dominus Contubernium",
            "shortcuts": ["XIII 2D"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          }],
          "name": "Second Cohort",
          "sheetName": "XIII 2C",
          "slots": [{
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 16,
              "row": 25,
              "sheetName": "Legio XIII"
            },
            "rank": "Centurion",
            "title": "Second Centurion"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 16,
              "row": 29,
              "sheetName": "Legio XIII"
            },
            "rank": "Optio",
            "title": "Second Optio"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 16,
              "row": 33,
              "sheetName": "Legio XIII"
            },
            "rank": "Signifer",
            "title": "Second Signifer"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 4,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "Second Aquilia & Bellum Tesserarius"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 16,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "Second Caesar & Dominus Tesserarius"
          }]
        },
        {
          "children": [{
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "Third Aquilia Contubernium",
            "shortcuts": ["XIII 3A"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 4
            },
            "name": "Third Bellum Contubernium",
            "shortcuts": ["XIII 3B"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "Third Caesar Contubernium",
            "shortcuts": ["XIII 3C"],
            "useSlotsFrom": "STANDARD_CONTUBERNIUM"
          },
          {
            "layout": "SQUAD_OFFSETS",
            "location": {
              "startCol": 16
            },
            "name": "Third Dominus Contubernium",
            "shortcuts": ["XIII 3D"],
            "useSlotsFrom": "CONTUBERNIUM_LOW"
          }],
          "name": "Third Cohort",
          "sheetName": "XIII 3C",
          "slots": [{
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 25,
              "row": 25,
              "sheetName": "Legio XIII"
            },
            "rank": "Centurion",
            "title": "Third Centurion"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 25,
              "row": 29,
              "sheetName": "Legio XIII"
            },
            "rank": "Optio",
            "title": "Third Optio"
          },
          {
            "layout": "BILLET_OFFSETS",
            "location": {
              "col": 25,
              "row": 33,
              "sheetName": "Legio XIII"
            },
            "rank": "Signifer",
            "title": "Third Signifer"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 4,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "Third Aquilia & Bellum Tesserarius"
          },
          {
            "layout": "BILLET_NCO_OFFSETS",
            "location": {
              "col": 16,
              "row": 7
            },
            "rank": "Tesserarius",
            "title": "Third Caesar & Dominus Tesserarius"
          }]
        }],
        "layout": "BILLET_OFFSETS",
        "name": "Legio XIII",
        "sheetName": "Legio XIII",
        "slots": [{
          "layout": "BILLET_OFFSETS",
          "location": {
            "col": 16,
            "row": 6
          },
          "rank": "Legatus",
          "title": "Legatus"
        },
        {
          "count": 2,
          "layout": "BILLET_OFFSETS",
          "locations": [{
            "col": 7,
            "row": 10
          },
          {
            "col": 25,
            "row": 10
          }],
          "rank": "Tribunus",
          "title": "Tribunus"
        },
        {
          "layout": "BILLET_OFFSETS",
          "location": {
            "col": 16,
            "row": 14
          },
          "rank": "Primus Pilus",
          "title": "Primus Pilus"
        },
        {
          "layout": "BILLET_OFFSETS",
          "location": {
            "col": 16,
            "row": 18
          },
          "rank": "Aquilifer",
          "title": "Aquilifer"
        }]
      }
    ],
      
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
        "rank": "Consul",
        "title": "Consul"
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