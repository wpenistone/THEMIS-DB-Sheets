const VERSION = "2.5x";
const _sheetIdCache = {};
let a_hasUrlFetchPermission = null;
let a_configIndexes = null;
let a_pathToShortcutMap = null;
let a_nodeNameToShortcutMap = null;
let USE_ADVANCED_API_FOR_READING = false;

const SCRIPT_STATUS = {
    SUCCESS: "SUCCESS",
    ERROR: "ERROR",
    NEEDS_CONFIRMATION: "NEEDS_CONFIRMATION"
};

const COLORS = {
    GREEN: 4919104,
    BLUE: 2201331,
    AMBER: 16761095,
    RED: 15942454
};
function onOpen() {
    Astraea_Ascendit();
}

function _Hestia_Visit_Domos(hierarchy, nodeCallback, path = []) {
    hierarchy.forEach(node => {
        const currentPath = [...path, node];
        nodeCallback(node, currentPath);
        if (node.children) _Hestia_Visit_Domos(node.children, nodeCallback, currentPath);
    });
}

function memoize(func) {
    let cache = null;
    return () => cache || (cache = func());
}

function _Maia_Investigat_Progeniem(path, propertyName) {
    if (!path || path.length === 0) {
        return null;
    }

    for (let i = path.length - 1; i >= 0; i--) {
        const node = path[i];
        if (node[propertyName] !== undefined && node[propertyName] !== null) {
            return node[propertyName];
        }
    }
    return null;
}
function _Hermes_Interpretatur_Notam(note) {
    if (!note || typeof note !== 'string') {
        return null;
    }
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
    const match = note.match(emailRegex);
    return match ? match[0] : null;
}

function _Themis_Praescribit_Legem(config) {
    const layoutName = config.slot.layout || _Maia_Investigat_Progeniem(config.fullPath, 'layout');
    const layout = THEMIS_CONFIG.LAYOUT_BLUEPRINTS[layoutName];
    if (!layout) throw new Error(`Layout "${layoutName}" not found.`);
    return layout;
}

function _Delphicum_Oraculum_ConsulitForLogging(userEmail) {
    const userData = _Delphicum_Oraculum_Consulit(userEmail);
    return userData ? `${userData.player} (${userEmail})` : userEmail;
}

function _Janus_Spectat_Cellam(sheetData, row, col, type = 'values') {
    if (!sheetData || !sheetData[type]) return null;
    const r = row - 1, c = col - 1;
    return (sheetData[type][r] && sheetData[type][r][c] !== undefined) ? sheetData[type][r][c] : null;
}

function createBaseEmbed(title, color, description = null, fields = []) {
    return {
        title,
        color,
        description,
        fields,
        footer: { text: `THEMIS v${VERSION}` },
        timestamp: new Date().toISOString(),
        author: { name: 'THEMIS System' }
    };
}

function handleError(funcName, error, user) {
    Aletheia_Testatur('ERROR', funcName, { message: error.message, stack: error.stack, user });
    return { status: SCRIPT_STATUS.ERROR, message: error.message };
}

function Astraea_Ascendit() {

    if (!_Terminus_Defendit_Fines()) {
        return;
    }

    const ui = SpreadsheetApp.getUi();
    try {
        ui.createMenu('THEMIS')
            .addItem('Manage', 'Porta_Monstrat_Tableau')
            .addItem('Recruit', 'Porta_Monstrat_Dilectum')
            .addItem('Log Event', 'Porta_Monstrat_Eventum')
            .addItem('Validate Attendance', 'Rhadamanthus_Initat_Iudicium')
            .addSeparator()
            .addItem('About', 'Porta_Monstrat_Gnosin')
            .addToUi();
    } catch (e) {
        ui.createMenu('THEMIS')
            .addItem('Error', 'Alecto_Clamat')
            .addToUi();
    }
}
const _getConfigIndexes = memoize(() => {
    const sourceIdToConfig = new Map();
    const locationPathToNode = new Map();

    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node, path) => {
        const currentPath = path.map(n => n.name).join('>');
        locationPathToNode.set(currentPath, node);

        const parentNode = path.length > 1 ? path[path.length - 2] : null; 
        const currentSheetName = _Maia_Investigat_Progeniem(path, 'sheetName');

        let slotsToProcess = [];
        const blueprintName = node.useSlotsFrom;
        if (blueprintName && THEMIS_CONFIG.SLOT_BLUEPRINTS[blueprintName]) {
            slotsToProcess = THEMIS_CONFIG.SLOT_BLUEPRINTS[blueprintName];
        } else if (node.slots) {
            slotsToProcess = node.slots;
        }

        for (const slot of slotsToProcess) {
            const effectiveSheetName = slot.location?.sheetName || currentSheetName;
            const processLocation = (row, col) => {
                const identifier = `${effectiveSheetName}|${row}|${col}`;
                sourceIdToConfig.set(identifier, {
                    node,
                    slot,
                    path: currentPath,
                    fullPath: path, 
                    parentNode,
                    sheetName: effectiveSheetName
                });
            };

            const startCol = node.location?.startCol || slot.location?.col;
            if (slot.locations) {
                slot.locations.forEach(loc => processLocation(loc.row, loc.col));
            } else if (slot.location && startCol !== undefined) {
                let allRows = [];
                if (slot.location.rows) allRows = slot.location.rows;
                else if (slot.location.row) allRows.push(slot.location.row);
                else if (slot.location.startRow && slot.location.endRow) {
                    for (let i = slot.location.startRow; i <= slot.location.endRow; i++) allRows.push(i);
                }
                allRows.forEach(row => processLocation(row, startCol));
            }
        }
    });

    return { sourceIdToConfig, locationPathToNode };
});
const _getNodeNameToShortcutMap = memoize(() => {
    const map = new Map();

    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node) => {
        if (node.shortcuts && node.shortcuts.length > 0) {
            map.set(node.name, node.shortcuts[0]);
        }
    });

    return map;
});

function _getFullPathToAbbreviatedPath(fullPath) {
    if (!fullPath) return fullPath;

    const shortcutMap = _getNodeNameToShortcutMap();
    const pathParts = fullPath.split('>');

    const abbreviatedParts = pathParts.map(part => {
        return shortcutMap.get(part) || part; 
    });

    return abbreviatedParts.join('>');
}
const _getPathToShortcutMap = memoize(() => {
    const map = new Map();

    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node, path) => {
        const currentPath = path.map(n => n.name).join('>');
        if (node.shortcuts && node.shortcuts.length > 0) {
            map.set(currentPath, node.shortcuts[0]);
        }
    });

    return map;
});

function _getDisplaySectionName(fullPath) {
    if (!fullPath) return 'N/A';
    const shortcutMap = _getPathToShortcutMap();
    if (shortcutMap.has(fullPath)) {
        return shortcutMap.get(fullPath);
    }
    return fullPath.split('>').pop();
}
function _Terminus_Defendit_Fines() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const requiredSheets = new Set();

    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node) => {
        if (node.sheetName) requiredSheets.add(node.sheetName);
    });

    requiredSheets.add(THEMIS_CONFIG.RECRUITMENT_LOG_SHEET_NAME);

    const allSheetNames = new Set(ss.getSheets().map(sheet => sheet.getName()));
    const missingSheets = [...requiredSheets].filter(sheetName => !allSheetNames.has(sheetName));

    if (missingSheets.length > 0) {
        const message = `The following required sheets are missing or have been renamed: \n\n- ${missingSheets.join('\n- ')}\n\nThe THEMIS tool will not function correctly until this is fixed.`;
        SpreadsheetApp.getUi().alert('THEMIS Configuration Error', message, SpreadsheetApp.getUi().ButtonSet.OK);
        return false;
    }
    return true;
}

function Alecto_Clamat() {
    SpreadsheetApp.getUi().alert('An error occurred while loading the add-on. Please try again later.');
}

function Porta_Monstrat_Tableau() {
    const html = HtmlService.createTemplateFromFile('ManagementDialog.html');
    SpreadsheetApp.getUi().showModalDialog(html.evaluate().setWidth(480).setHeight(455), ' ');
}

function Porta_Monstrat_Dilectum() {
    const html = HtmlService.createTemplateFromFile('RecruitDialog.html');
    SpreadsheetApp.getUi().showModalDialog(html.evaluate().setWidth(480).setHeight(494), ' ');
}

function Porta_Monstrat_Eventum() {
    const html = HtmlService.createTemplateFromFile('EventDialog.html');
    SpreadsheetApp.getUi().showModalDialog(html.evaluate().setWidth(500).setHeight(700), ' ');
}

function Porta_Monstrat_Gnosin() {
    const html = HtmlService.createHtmlOutputFromFile('AboutDialog.html').setWidth(400).setHeight(500);
    SpreadsheetApp.getUi().showModalDialog(html, 'About THEMIS');
}

function Rhadamanthus_Initat_Iudicium() {
    const ui = SpreadsheetApp.getUi();
    const response = ui.alert('Warning!', 'This will check all names in the Attendance Sheet for validity. This can be resource intensive.\n Proceed?', ui.ButtonSet.YES_NO);
    if (response !== ui.Button.YES) return;

    const result = _Rhadamanthus_Inspectat_Nomina();
    if (result.status === SCRIPT_STATUS.ERROR) {
        return ui.alert("Error", result.message, ui.ButtonSet.OK);
    }
    if (result.invalidNames.length === 0) {
        return ui.alert("Validation Complete", "All attendee names found.", ui.ButtonSet.OK);
    }

    const template = HtmlService.createTemplateFromFile('ValidationResults');
    template.data = {
        invalidNamesList: result.invalidNames.join('\n'),
        count: result.invalidNames.length
    };
    const html = template.evaluate().setWidth(400).setHeight(350);
    ui.showModalDialog(html, `Validation Results (${result.invalidNames.length} Invalid Names Found)`);
}
function Fama_Susurrat(message, title, timeoutSeconds) {
  SpreadsheetApp.getActiveSpreadsheet().toast(message, title, timeoutSeconds);
}
function getFormattedDateString(date) {
    if (!(date instanceof Date) || isNaN(date)) {
        return "";
    }
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const year = date.getFullYear();
    const shortYear = year.toString().slice(-2);

    switch (THEMIS_CONFIG.DATE_FORMAT) {
        case "DD/MM/YY":
            return `${day}/${month}/${shortYear}`;
        case "YYYY-MM-DD":
            return `${year}-${month}-${day}`;
        case "MM/DD/YY":
        default:
            return `${month}/${day}/${shortYear}`;
    }
}

function _getRankIndex(rank) {
    if (!rank) return -1;
    const upperRank = String(rank).toUpperCase().trim();
    const index = THEMIS_CONFIG.RANK_HIERARCHY.findIndex(r =>
        r.name.toUpperCase() === upperRank ||
        (r.abbr && r.abbr.toUpperCase() === upperRank)
    );
    return index !== -1 ? index : THEMIS_CONFIG.RANK_HIERARCHY.length;
}

function _isEmailRequiredForRank(rankName) {
    const config = THEMIS_CONFIG.LOGIC_THRESHOLDS.EMAIL_REQUIRED_MIN_RANK;
    if (!config || !config.CONDITION) return false;

    const condition = config.CONDITION.trim();
    const rankHierarchy = THEMIS_CONFIG.RANK_HIERARCHY;

    const selectedRankIndex = rankHierarchy.findIndex(r => r.name === rankName);
    if (selectedRankIndex === -1) return false;

    if (condition.includes(',')) {
        const requiredRanks = condition.split(',').map(r => r.trim().toUpperCase());
        const selectedRankInfo = rankHierarchy[selectedRankIndex];
        const selectedRankNames = [selectedRankInfo.name.toUpperCase()];
        if (selectedRankInfo.abbr) selectedRankNames.push(selectedRankInfo.abbr.toUpperCase());
        return requiredRanks.some(reqRank => selectedRankNames.includes(reqRank));
    }

    const match = condition.match(/^(>=|<=|>|<|=)?\s*(.*)$/);
    if (!match) return false;

    const operator = match[1] || '>=';
    const compareRankName = match[2];

    const compareRankIndex = rankHierarchy.findIndex(r => r.name.toUpperCase() === compareRankName.toUpperCase() || (r.abbr && r.abbr.toUpperCase() === compareRankName.toUpperCase()));
    if (compareRankIndex === -1) return false;

    switch (operator) {
        case '>=': return selectedRankIndex >= compareRankIndex;
        case '>':  return selectedRankIndex > compareRankIndex;
        case '<=': return selectedRankIndex <= compareRankIndex;
        case '<':  return selectedRankIndex < compareRankIndex;
        case '=':  return selectedRankIndex === compareRankIndex;
        default: return false;
    }
}

function _findNodeAndPathByPathIdentifier(pathIdentifier, hierarchy = THEMIS_CONFIG.ORGANIZATION_HIERARCHY, currentPath = []) {
    if (!pathIdentifier) return null;
    const pathParts = pathIdentifier.split('>');

    let nodesToSearch = hierarchy;
    let foundNode = null;
    let finalPath = [];

    for (const part of pathParts) {
        foundNode = nodesToSearch.find(node => node.name === part);
        if (foundNode) {
            finalPath.push(foundNode);
            nodesToSearch = foundNode.children || [];
        } else {
            return null; 
        }
    }

    if (foundNode) {
        return { node: foundNode, path: finalPath };
    }
    return null;
}
function _getSectionNameForLogging(fullPath) {
    if (!fullPath) return 'N/A';

    const result = _findNodeAndPathByPathIdentifier(fullPath);
    if (!result) return _getDisplaySectionName(fullPath); 

    const useShortName = _Maia_Investigat_Progeniem(result.path, 'logShortSectionName');

    if (useShortName) {
        return _getDisplaySectionName(fullPath); 
    } else {
        return _getFullPathToAbbreviatedPath(fullPath); 
    }
}
function findNodeAndPath(nodeName, hierarchy = THEMIS_CONFIG.ORGANIZATION_HIERARCHY, path = []) {
    for (const node of hierarchy) {
        const currentPath = [...path, node];
        if (node.name.toLowerCase() === nodeName.toLowerCase()) {
            return {
                node: node,
                path: currentPath
            };
        }
        if (node.children && node.children.length > 0) {
            const result = findNodeAndPath(nodeName, node.children, currentPath);
            if (result) return result;
        }
    }
    return null;
}

function _getNodeSettings(nodeName) {
    let finalSettings = {}; 
    const result = findNodeAndPath(nodeName);
    if (!result) {
        return finalSettings;
    }
    for (const nodeInPath of result.path) {
        if (nodeInPath.settings) {

            Object.assign(finalSettings, nodeInPath.settings);
        }
    }
    return finalSettings;
}

const _getStructureFromHierarchy = memoize(() => {
    const groups = {};
    const groupOrder = [];

    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node, path) => {
        const currentPath = path.map(n => n.name).join('>');
        const isBilletHQ = node.slots && node.slots.some(slot => slot.layout === 'BILLET_OFFSETS');
        const hasSquads = node.children && node.children.some(child => child.layout === 'SQUAD_OFFSETS');

        if (isBilletHQ || hasSquads) {
            groupOrder.push(currentPath);
            groups[currentPath] = node.children ? node.children.map(child => `${currentPath}>${child.name}`) : [];
        }
    });

    return { groups, groupOrder };
});

function _resolveSectionShortcut(shortcut) {
    if (!shortcut) return null;
    const lowerCaseShortcut = shortcut.toLowerCase();
    let foundPath = null;

    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node, path) => {
        if (foundPath) return;
        if (node.shortcuts && node.shortcuts.some(s => s.toLowerCase() === lowerCaseShortcut)) {
            foundPath = path.map(n => n.name).join('>');
        }
    });

    return foundPath;
}

function _getCommandCellCoordinates(rankKey) {
    let targetSlot = null;

    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node) => {
        if (targetSlot) return;
        if (node.slots) {
            targetSlot = node.slots.find(s => s.title === rankKey);
        }
    });

    if (!targetSlot) {
        Aletheia_Testatur('ERROR', 'getCommandCellCoordinates', `Could not find a billet slot for rankKey: ${rankKey}`);
        return null;
    }

    const layout = THEMIS_CONFIG.LAYOUT_BLUEPRINTS[targetSlot.layout];
    if (!layout || !layout.offsets) {
        Aletheia_Testatur('ERROR', 'getCommandCellCoordinates', `Could not find layout or offsets for slot with rankKey: ${rankKey}`);
        return null;
    }

    const offsets = layout.offsets;
    const baseRow = targetSlot.location.row;
    const baseCol = targetSlot.location.col;

    return {
        username: {
            row: baseRow + (offsets.username?.row || 0),
            col: baseCol + (offsets.username?.col || 0)
        },
        region: {
            row: baseRow + (offsets.region?.row || 0),
            col: baseCol + (offsets.region?.col || 0)
        },
        joinDate: {
            row: baseRow + (offsets.joinDate?.row || 0),
            col: baseCol + (offsets.joinDate?.col || 0)
        },
        discordId: {
            row: baseRow + (offsets.discordId?.row || 0),
            col: baseCol + (offsets.discordId?.col || 0)
        },
        checkbox: {
            row: baseRow + (offsets.checkbox?.row || 0),
            col: baseCol + (offsets.checkbox?.col || 0)
        }
    };
}
function _groupContiguousColumns(columns) {
    if (!columns || columns.length === 0) {
        return [];
    }

    const sorted = [...new Set(columns)].sort((a, b) => a - b);
    const groups = [];
    if (sorted.length === 0) return groups;

    let currentGroup = [sorted[0]];
    for (let i = 1; i < sorted.length; i++) {
        if (sorted[i] === sorted[i - 1] + 1) {
            currentGroup.push(sorted[i]);
        } else {
            groups.push(currentGroup);
            currentGroup = [sorted[i]];
        }
    }
    groups.push(currentGroup);
    return groups;
}
function _columnToLetter(column) {
    let temp, letter = '';
    while (column > 0) {
        temp = (column - 1) % 26;
        letter = String.fromCharCode(temp + 65) + letter;
        column = (column - temp - 1) / 26;
    }
    return letter;
}

function _getEffectiveValue(cellData) {
    if (!cellData || !cellData.userEnteredValue) {
        return null; 
    }
    const userEnteredValue = cellData.userEnteredValue;
    if ('stringValue' in userEnteredValue) return userEnteredValue.stringValue;
    if ('numberValue' in userEnteredValue) return userEnteredValue.numberValue;
    if ('boolValue' in userEnteredValue) return userEnteredValue.boolValue;
    if ('formulaValue' in userEnteredValue) return userEnteredValue.formulaValue;
    return null;
}

let a_sheetDataCache = new Map();

function invalidateSpecificSheetCaches(sheetNames) {
    if (!sheetNames || sheetNames.length === 0) return;

    const uniqueSheetNames = [...new Set(sheetNames)];

    const cache = CacheService.getScriptCache();
    const keysToRemove = uniqueSheetNames.map(name => `${THEMIS_CONFIG.CACHE_KEYS.SHEET_DATA_PREFIX}${name}`);

    uniqueSheetNames.forEach(name => a_sheetDataCache.delete(name));

    cache.removeAll(keysToRemove);
    Logger.log(`Invalidated specific sheet caches for: ${uniqueSheetNames.join(', ')}`);
}
function _Epimetheus_Struit(sheetNamesToEnsure) {
    const sheetsToFetch = sheetNamesToEnsure.filter(name => !a_sheetDataCache.has(name) && name);
    if (sheetsToFetch.length === 0) return;

    if (!USE_ADVANCED_API_FOR_READING) {
        Logger.log(`Using Standard API to fetch sheets: ${sheetsToFetch.join(', ')}`);
        const ss = SpreadsheetApp.getActiveSpreadsheet();
        for (const sheetName of sheetsToFetch) {
            const sheet = ss.getSheetByName(sheetName);
            if (!sheet) {
                a_sheetDataCache.set(sheetName, { values: [], notes: [] });
                continue;
            }

            let values = [];
            let notes = [];

            try {
                const dataRange = sheet.getDataRange();
                values = dataRange.getValues();
                notes = dataRange.getNotes();
            } catch (e) {
                Logger.log(`Sheet "${sheetName}" appears to be empty. Skipping data read for it.`);
            }

            const dataObject = { values, notes };
            a_sheetDataCache.set(sheetName, dataObject);

            try {
                const jsonString = JSON.stringify(dataObject);
                if (jsonString.length > 1000) {
                    const blob = Utilities.newBlob(jsonString, 'application/json');
                    const zippedBlob = Utilities.zip([blob]);
                    const zippedBase64 = Utilities.base64Encode(zippedBlob.getBytes());
                    const cacheKey = `${THEMIS_CONFIG.CACHE_KEYS.SHEET_DATA_PREFIX}${sheetName}`;
                    CacheService.getScriptCache().put(cacheKey, zippedBase64, THEMIS_CONFIG.CACHE_DURATIONS.LONG);
                }
            } catch(e) {
                Logger.log(`Warning: Could not save sheet "${sheetName}" to persistent cache (Standard API). Error: ${e.message}`);
            }
        }
        return; 
    }
    const spreadsheetId = SpreadsheetApp.getActiveSpreadsheet().getId();
    try {
        const response = Sheets.Spreadsheets.get(spreadsheetId, {
            ranges: sheetsToFetch,
            fields: 'sheets(properties.title,data(rowData(values(userEnteredValue,note))))'
        });

        if (response.sheets) {
            for (const sheetData of response.sheets) {
                const sheetName = sheetData.properties.title;
                const valuesForSheet = [], notesForSheet = [], rowData = sheetData.data?.[0]?.rowData || [];
                let maxCols = 0;

                rowData.forEach(row => { if (row.values && row.values.length > maxCols) maxCols = row.values.length; });

                for (const row of rowData) {
                    const valueRow = new Array(maxCols).fill(null);
                    const noteRow = new Array(maxCols).fill(null);
                    if (row.values) {
                        for (let c = 0; c < row.values.length; c++) {
                            const cell = row.values[c];
                            if (cell) {
                                valueRow[c] = _getEffectiveValue(cell);
                                noteRow[c] = cell.note || null;
                            }
                        }
                    }
                    valuesForSheet.push(valueRow);
                    notesForSheet.push(noteRow);
                }

                const dataObject = { values: valuesForSheet, notes: notesForSheet };
                a_sheetDataCache.set(sheetName, dataObject);

                try {
                    const jsonString = JSON.stringify(dataObject);
                    if (jsonString.length > 1000) { 
                        const blob = Utilities.newBlob(jsonString, 'application/json');
                        const zippedBlob = Utilities.zip([blob]);
                        const zippedBase64 = Utilities.base64Encode(zippedBlob.getBytes());
                        const cacheKey = `${THEMIS_CONFIG.CACHE_KEYS.SHEET_DATA_PREFIX}${sheetName}`;
                        CacheService.getScriptCache().put(cacheKey, zippedBase64, THEMIS_CONFIG.CACHE_DURATIONS.LONG);
                    }
                } catch(e) {
                    Logger.log(`Warning: Could not save sheet "${sheetName}" to persistent cache. Error: ${e.message}`);
                }
            }
        }
    } catch (e) {
        Logger.log(`CRITICAL ERROR in _Epimetheus_Struit: ${e.message}\n${e.stack}`);
        throw new Error("Failed to read sheet data using Advanced API.");
    }
}

function _Prometheus_Acquirit_Ignem(requiredSheetNames) {
    const sheetsNeededFromPersistentCache = requiredSheetNames.filter(name => name && !a_sheetDataCache.has(name));

    if (sheetsNeededFromPersistentCache.length > 0) {
        const cache = CacheService.getScriptCache();
        const cacheKeys = sheetsNeededFromPersistentCache.map(name => `${THEMIS_CONFIG.CACHE_KEYS.SHEET_DATA_PREFIX}${name}`);
        const cachedItems = cache.getAll(cacheKeys);

        for (const name of sheetsNeededFromPersistentCache) {
            const cacheKey = `${THEMIS_CONFIG.CACHE_KEYS.SHEET_DATA_PREFIX}${name}`;
            const cachedValue = cachedItems[cacheKey];
            if (cachedValue) {
                try {
                    const unzippedBytes = Utilities.base64Decode(cachedValue);
                    const unzippedBlob = Utilities.newBlob(unzippedBytes).setContentType('application/zip');
                    const unzippedJson = Utilities.unzip(unzippedBlob)[0].getDataAsString();
                    a_sheetDataCache.set(name, JSON.parse(unzippedJson));
                } catch (e) {
                    Logger.log(`Could not decompress/parse cache for "${name}". Fetching live. Error: ${e.message}`);
                    cache.remove(cacheKey);
                }
            }
        }
    }

    _Epimetheus_Struit(requiredSheetNames);

    const result = new Map();
    for (const name of requiredSheetNames) {
        result.set(name, a_sheetDataCache.get(name) || { values: [], notes: [] });
    }
    return result;
}

function Nosce_Te_Ipsum() {
    const userEmail = getCurrentUserEmail();
    const userData = _Delphicum_Oraculum_Consulit(userEmail);

    if (!userData) {
        SpreadsheetApp.getActiveSpreadsheet().toast(
            `User profile (${userEmail}) not found. Some features may be limited.`,
            'THEMIS Notice',
            8
        );
    }
    return userData; 
}
function _getSheetId(ss, sheetName) {
    const cacheKey = ss.getId() + sheetName;
    if (_sheetIdCache[cacheKey]) {
        return _sheetIdCache[cacheKey];
    }
    const sheet = ss.getSheetByName(sheetName);
    if (sheet) {
        const sheetId = sheet.getSheetId();
        _sheetIdCache[cacheKey] = sheetId;
        return sheetId;
    }
    throw new Error(`Sheet with name "${sheetName}" not found.`);
}


function _parseLoaNote(note) {
    if (!note || !note.trim()) {
        return null;
    }

    const mainRegex = /Start Date: (.*?)\nEnd Date: (.*?)\nReason: ([\s\S]*)/;
    let match = note.match(mainRegex);

    if (match) {
        const startDate = match[1].trim();
        const endDate = match[2].trim();
        let fullReasonBlock = match[3].trim();
        let reason = fullReasonBlock;
        let setBy = 'N/A';
        const bySeparatorIndex = fullReasonBlock.search(/\n\s*(\u200B\s*)?\n*\s*By:/);

        if (bySeparatorIndex !== -1) {
            reason = fullReasonBlock.substring(0, bySeparatorIndex).trim();
            const byLine = fullReasonBlock.substring(bySeparatorIndex).trim();
            setBy = byLine.replace(/(\u200B\s*)?\n*\s*By:\s*/, '').trim();
        }
        return { startDate, endDate, reason, setBy };
    }

    const dateRegex = /\b((\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4})|(\d{4}[\/-]\d{1,2}[\/-]\d{1,2}))\b/g;
    const dateMatches = [...note.matchAll(dateRegex)];
    
    const validDates = dateMatches.map(m => {
        const dateString = m[0].trim();
        const formatPriority = [THEMIS_CONFIG.DATE_FORMAT, "MM/DD/YY", "DD/MM/YY", "YYYY-MM-DD", "MM/DD/YYYY"];
        const uniqueFormats = [...new Set(formatPriority)];

        for (const format of uniqueFormats) {
            try {
                let parts;
                let month, day, year;
                if (format.includes('/')) parts = dateString.split('/');
                else if (format.includes('-')) parts = dateString.split('-');
                else continue;
                if (parts.length !== 3) continue;

                switch (format) {
                    case "DD/MM/YY": case "DD/MM/YYYY":
                        day = parseInt(parts[0], 10); month = parseInt(parts[1], 10) - 1; year = parseInt(parts[2], 10); break;
                    case "YYYY-MM-DD":
                        year = parseInt(parts[0], 10); month = parseInt(parts[1], 10) - 1; day = parseInt(parts[2], 10); break;
                    case "MM/DD/YY": case "MM/DD/YYYY":
                    default:
                        month = parseInt(parts[0], 10) - 1; day = parseInt(parts[1], 10); year = parseInt(parts[2], 10); break;
                }

                if (isNaN(day) || isNaN(month) || isNaN(year)) continue;
                if (year < 100) year += 2000;
                
                const date = new Date(Date.UTC(year, month, day));
                if (date.getUTCFullYear() === year && date.getUTCMonth() === month && date.getUTCDate() === day) {
                    return date; 
                }
            } catch (e) {}
        }
        return null; 
    }).filter(d => d !== null); 

    if (validDates.length >= 2) {
        validDates.sort((a, b) => a.getTime() - b.getTime()); 

        const startDateObj = validDates[0];
        const endDateObj = validDates[1];

        let remainingText = note;
        dateMatches.forEach(m => { remainingText = remainingText.replace(m[0], ''); });
        let reason = remainingText.replace(/Start Date:|End Date:|Reason:|By:/gi, '').replace(/\n\s*\n/g, '\n').trim();
        let setBy = 'N/A';
        const byMatch = reason.match(/(.*?)\s*By:\s*(.*)/is);
        if (byMatch) {
            reason = byMatch[1].trim();
            setBy = byMatch[2].trim();
        }

        return {
            startDate: getFormattedDateString(startDateObj),
            endDate: getFormattedDateString(endDateObj),
            reason: reason || "No reason provided.",
            setBy: setBy
        };
    }

    if (note.trim().startsWith('{')) {
        try { return JSON.parse(note); } catch (e) { }
    }

    return null;
}

function _Chronos_Interpretatur(dateString) {
    if (!dateString || typeof dateString !== 'string') return null;

    try {
        const trimmedDate = dateString.trim();
        let parts;
        let month, day, year;

        switch(THEMIS_CONFIG.DATE_FORMAT) {
            case "DD/MM/YY":
                parts = trimmedDate.split('/');
                if (parts.length !== 3) return null;
                day = parseInt(parts[0], 10);
                month = parseInt(parts[1], 10) - 1;
                year = parseInt(parts[2], 10);
                break;

            case "YYYY-MM-DD":
                parts = trimmedDate.split('-');
                if (parts.length !== 3) return null;
                year = parseInt(parts[0], 10);
                month = parseInt(parts[1], 10) - 1;
                day = parseInt(parts[2], 10);
                break;

            case "MM/DD/YY":
            default:
                parts = trimmedDate.split('/');
                if (parts.length !== 3) return null;
                month = parseInt(parts[0], 10) - 1;
                day = parseInt(parts[1], 10);
                year = parseInt(parts[2], 10);
                break;
        }

        if (parts.length !== 3) return null;

        if (year < 100 && THEMIS_CONFIG.DATE_FORMAT.includes("YY") && !THEMIS_CONFIG.DATE_FORMAT.includes("YYYY")) { 
            year += 2000;
        }

        const date = new Date(year, month, day);

        if (date.getFullYear() === year && date.getMonth() === month && date.getDate() === day) {
            return date;
        }
        return null;
    } catch (e) {
        return null;
    }
}

function _Clio_Scribit_Catalogum() {

    const rankMap = new Map();
    THEMIS_CONFIG.RANK_HIERARCHY.forEach(rank => {
        rankMap.set(rank.name.toUpperCase(), rank.name);
        if (rank.abbr) {
            rankMap.set(rank.abbr.toUpperCase(), rank.name);
        }
    });

    const allSlotTasks = [];
    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node, path) => {
        const currentPath = path.map(n => n.name).join('>');
        const currentSheetName = _Maia_Investigat_Progeniem(path, 'sheetName');
        const layoutName = _Maia_Investigat_Progeniem(path, 'layout');

        let slotsToProcess = [];
        const blueprintName = node.useSlotsFrom;
        if (blueprintName && THEMIS_CONFIG.SLOT_BLUEPRINTS[blueprintName]) {
            slotsToProcess = THEMIS_CONFIG.SLOT_BLUEPRINTS[blueprintName];
        } else if (node.slots) {
            slotsToProcess = node.slots;
        }

        for (const slot of slotsToProcess) {
            const effectiveSheetName = slot.location?.sheetName || currentSheetName;
            const effectiveLayoutName = slot.layout || layoutName;
            const isBillet = effectiveLayoutName === 'BILLET_OFFSETS';

            const locations = [];
            const startCol = node.location?.startCol || slot.location?.col;

            if (slot.locations) {
                locations.push(...slot.locations);
            } else if (slot.location && startCol !== undefined) {
                let allRows = [];
                if (slot.location.rows) allRows = slot.location.rows;
                else if (slot.location.row) allRows.push(slot.location.row);
                else if (slot.location.startRow && slot.location.endRow) {
                    for (let i = slot.location.startRow; i <= slot.location.endRow; i++) allRows.push(i);
                }
                allRows.forEach(row => locations.push({ row, col: startCol }));
            }

            locations.forEach(loc => {
                allSlotTasks.push({
                    row: loc.row, col: loc.col, sheetName: effectiveSheetName,
                    layoutName: effectiveLayoutName, isBillet: isBillet,
                    node: { name: node.name }, slot: { title: slot.title, rank: slot.rank, ranks: slot.ranks },
                    path: currentPath, blueprintName: blueprintName
                });
            });
        }
    });

    const requiredSheetNames = [...new Set(allSlotTasks.map(task => task.sheetName).filter(Boolean))];
    const allSheetData = _Prometheus_Acquirit_Ignem(requiredSheetNames);

    const companymen = [];

    for (const task of allSlotTasks) {
        const sheetData = allSheetData.get(task.sheetName);
        if (!sheetData) continue;

        const layout = THEMIS_CONFIG.LAYOUT_BLUEPRINTS[task.layoutName];
        if (!layout) continue;

        const offsets = layout.offsets || {};
        const { row, col } = task;

        const userRow = row + (offsets.username?.row || 0);
        const userCol = col + (offsets.username?.col || 0);
        const usernameRaw = _Janus_Spectat_Cellam(sheetData, userRow, userCol, 'values');

        if (!usernameRaw || !String(usernameRaw).trim()) {
            continue;
        }

        const username = String(usernameRaw).trim();
        let rank;

        if (task.isBillet) {
            rank = task.slot.rank || (task.slot.ranks ? task.slot.ranks[0] : null);
        } else {
            const rankOnSheet = String(_Janus_Spectat_Cellam(sheetData, row + (offsets.rank?.row || 0), col + (offsets.rank?.col || 0), 'values') || '').toUpperCase();
            rank = rankMap.get(rankOnSheet);
        }

        if (rank) {
            const loaNote = _Janus_Spectat_Cellam(sheetData, row + (offsets.LOAcheckbox?.row || 0), col + (offsets.LOAcheckbox?.col || 0), 'notes');
            const joinDateRaw = _Janus_Spectat_Cellam(sheetData, row + (offsets.joinDate?.row || 0), col + (offsets.joinDate?.col || 0), 'values');
            const parsedJoinDate = joinDateRaw instanceof Date ? joinDateRaw : _Chronos_Interpretatur(joinDateRaw);
            const person = {
                player: username, rank: rank, location: task.node.name, locationPath: task.path,
                sheetName: task.sheetName, isHQ: task.isBillet, row: row, startCol: col,
                sourceIdentifier: `${task.sheetName}|${row}|${col}`,
                layoutName: task.layoutName,
                joinDate: parsedJoinDate ? Utilities.formatDate(parsedJoinDate, Session.getScriptTimeZone(), "yyyy-MM-dd") : null,
                email: _Hermes_Interpretatur_Notam(_Janus_Spectat_Cellam(sheetData, userRow, userCol, 'notes')),
                onLOA: _Janus_Spectat_Cellam(sheetData, row + (offsets.LOAcheckbox?.row || 0), col + (offsets.LOAcheckbox?.col || 0), 'values'),
                loaNote: loaNote, loaData: _parseLoaNote(loaNote),
                hasPassedUBT: !!_Janus_Spectat_Cellam(sheetData, row + (offsets.BTcheckbox?.row || 0), col + (offsets.BTcheckbox?.col || 0), 'values'),
                discordId: String(_Janus_Spectat_Cellam(sheetData, row + (offsets.discordId?.row || 0), col + (offsets.discordId?.col || 0), 'values') || '').replace(/\D/g, ''),
                region: String(_Janus_Spectat_Cellam(sheetData, row + (offsets.region?.row || 0), col + (offsets.region?.col || 0), 'values') || '').trim(),
                rankKey: task.slot.title || null, blueprint: task.blueprintName,
                customFields: {} 
            };

            if (THEMIS_CONFIG.CUSTOM_FIELDS) {
                THEMIS_CONFIG.CUSTOM_FIELDS.forEach(field => {
                    if (offsets[field.offsetKey]) {
                        const customData = {
                            value: _Janus_Spectat_Cellam(sheetData, row + offsets[field.offsetKey].row, col + offsets[field.offsetKey].col, 'values'),
                            note: field.transferNote ? _Janus_Spectat_Cellam(sheetData, row + offsets[field.offsetKey].row, col + offsets[field.offsetKey].col, 'notes') : null
                        };
                        if (customData.value) {
                            person.customFields[field.key] = customData;
                        }
                    }
                });
            }

            companymen.push(person);
        }
    }

    return companymen;
}

function Aletheia_Testatur(logType, functionName, details = {}) {
    try {
        const userEmail = details.user || getCurrentUserEmail();
        const userData = _Delphicum_Oraculum_Consulit(userEmail);
        const authorName = _Delphicum_Oraculum_ConsulitForLogging(userEmail);

        let logData;

        if (logType === 'ERROR') {
            logData = {
                functionName: functionName,
                error: details.message || 'No message provided.',
                stack: details.stack || 'No stack trace available.',
                authorName: authorName,
                authorData: userData 
            };
        } else {
            logData = (typeof details === 'object' && details !== null && !Array.isArray(details))
                ? { ...details, authorName: authorName, authorData: userData } 
                : { message: String(details), authorName: authorName, authorData: userData }; 
        }

        delete logData.user;

        const payload = _Iris_Format_Nuntium(logType, logData);
        if (payload) {
            _Charon_Accipit_Vecturam(payload);
        }

    } catch (e) {
        Logger.log(`Error in logging system: ${e.message} \n ${e.stack}`);
        try {
            const errorPayload = _Iris_Format_Nuntium('ERROR', { error: e.message, originalFunction: logType, originalFunctionName: functionName, authorName: 'System' });
            if (errorPayload) {
                _Charon_Accipit_Vecturam(errorPayload);
            }
        } catch (finalError) {
        }
    }
}

function _Iris_Volat(payload) {
    if (a_hasUrlFetchPermission === null) {
        a_hasUrlFetchPermission = true; 
    }

    if (!a_hasUrlFetchPermission) {
        return false;
    }

    const webhookUrl = THEMIS_CONFIG.WEBHOOK_URL;
    if (!webhookUrl || !webhookUrl.startsWith("https://discord.com/api/webhooks/")) {
        return true;
    }

    const options = {
        method: 'post',
        contentType: 'application/json',
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
    };

    try {
        const response = UrlFetchApp.fetch(webhookUrl, options);
        if (response.getResponseCode() >= 200 && response.getResponseCode() < 300) {
            return true; 
        } else {
            Logger.log(`Webhook send failed with status ${response.getResponseCode()}: ${response.getContentText()}`);
            return false; 
        }
    } catch (e) {
        Logger.log(`Critical error sending webhook. Error: ${e.message}`);

        if (e.message.includes('You do not have permission to call UrlFetchApp.fetch')) {
             a_hasUrlFetchPermission = false; 
             Logger.log("Permission denied. All subsequent webhook calls in this execution will be skipped and queued.");
        }

        return false; 
    }
}
function _processWebhookRetryQueue() {
    const cache = CacheService.getScriptCache();
    const cacheKey = 'webhook_retry_queue_v1';

    const cachedQueue = cache.get(cacheKey);
    if (!cachedQueue) {
        return; 
    }

    let queue;
    try {
        queue = JSON.parse(cachedQueue);
    } catch (e) {
        Logger.log("Could not parse webhook retry queue. Clearing invalid data.");
        cache.remove(cacheKey);
        return;
    }

    if (!Array.isArray(queue) || queue.length === 0) {
        return; 
    }

    const remainingItems = []; 

    for (const payload of queue) {
        const success = _Iris_Volat(payload);
        if (!success) {
            remainingItems.push(payload);
        }
    }

    if (remainingItems.length > 0) {
        cache.put(cacheKey, JSON.stringify(remainingItems), 21600); 
    } else {
        cache.remove(cacheKey);
    }
}
function _Hades_Catalogit_Animam(deletedPerson) {
    const fields = [];
    const customFieldConfigMap = new Map((THEMIS_CONFIG.CUSTOM_FIELDS || []).map(f => [f.key, f]));

    fields.push({ name: 'Player', value: deletedPerson.player, inline: true });
    fields.push({ name: 'Rank', value: deletedPerson.rank, inline: true });
    fields.push({ name: 'Assignment', value: _getDisplaySectionName(deletedPerson.locationPath), inline: true });

    if (deletedPerson.discordId) {
        fields.push({ name: 'Discord User', value: `<@${deletedPerson.discordId}>`, inline: true });
    }
    if (deletedPerson.email) {
        fields.push({ name: 'Email', value: deletedPerson.email, inline: true });
    }
    if (deletedPerson.region) {
        fields.push({ name: 'Region', value: deletedPerson.region, inline: true });
    }
    if (deletedPerson.joinDate) {
        fields.push({ name: 'Join Date', value: deletedPerson.joinDate, inline: true });
    }

    const ubtName = THEMIS_CONFIG.UBT_SETTINGS.NAME || 'UBT';
    fields.push({ name: ubtName, value: deletedPerson.hasPassedUBT ? 'Passed' : 'Not Passed', inline: true });

    if (deletedPerson.onLOA && deletedPerson.loaData) {
        const loaDetails = `Start:  ${deletedPerson.loaData.startDate}\n` +
                           `End:    ${deletedPerson.loaData.endDate}\n` +
                           `Reason: ${deletedPerson.loaData.reason}`;

        fields.push({
            name: 'Final LOA Status (at time of deletion)',
            value: "```\n" + loaDetails + "\n```",
            inline: false 
        });
    }

    for (const key in deletedPerson.customFields) {
        const customData = deletedPerson.customFields[key];
        const value = customData.value ?? 'N/A';
        const config = customFieldConfigMap.get(key);
        const fieldName = config ? config.label : key; 
        fields.push({ name: fieldName, value: `\`${value}\``, inline: true });
    }

    return fields;
}
function _Hephaestus_Comparat_Mutationes(oldState, newState) {
    const fields = [];
    const customFieldConfigMap = new Map((THEMIS_CONFIG.CUSTOM_FIELDS || []).map(f => [f.key, f]));

    if (oldState.rank !== newState.rank) {
        fields.push({ name: 'Rank', value: `\`${oldState.rank}\` → \`${newState.rank}\``, inline: false });
    }
    if (oldState.locationPath !== newState.locationPath) {
        fields.push({ name: 'Assignment', value: `\`${_getDisplaySectionName(oldState.locationPath)}\` → \`${_getDisplaySectionName(newState.locationPath)}\``, inline: false });
    }
    if ((oldState.email || null) !== (newState.email || null)) {
        fields.push({ name: 'Email', value: `\`${oldState.email || 'None'}\` → \`${newState.email || 'None'}\``, inline: false });
    }
    if (!!oldState.hasPassedUBT !== !!newState.hasPassedUBT) {
        const ubtName = THEMIS_CONFIG.UBT_SETTINGS.NAME || 'UBT';
        fields.push({ name: ubtName, value: `\`${oldState.hasPassedUBT ? 'Passed' : 'Not Passed'}\` → \`${newState.hasPassedUBT ? 'Passed' : 'Not Passed'}\``, inline: false });
    }

    const allCustomFieldKeys = new Set([
        ...Object.keys(oldState.customFields || {}),
        ...Object.keys(newState.customFields || {})
    ]);

    allCustomFieldKeys.forEach(key => {
        const oldCustom = oldState.customFields?.[key];
        const newCustom = newState.customFields?.[key];

        const oldValue = oldCustom?.value ?? oldCustom ?? 'None';
        const newValue = newCustom?.value ?? newCustom ?? 'None';

        if (String(oldValue) !== String(newValue)) {
            const config = customFieldConfigMap.get(key);
            const fieldName = config ? config.label : key; 
            fields.push({ name: `Updated '${fieldName}'`, value: `\`${oldValue}\` → \`${newValue}\``, inline: false });
        }
    });

    return fields;
}
function _Iris_Format_Nuntium(functionName, data) {
    if (functionName === 'INFO') {
        return;
    }

    const editorWebhookUrl = THEMIS_CONFIG.WEBHOOK_URL;
    if (!editorWebhookUrl || !editorWebhookUrl.startsWith("https://discord.com/api/webhooks/")) {
        return;
    }

    const author = data.authorData;
    let authorString;
    let content = null;

    if (author && author.player) {
        const playerName = author.player;
        const email = author.email ? `(${author.email})` : '';
        authorString = `${playerName} ${email}`.trim();
    } else {
        authorString = data.authorName || 'System';
    }

    let embed;

    switch (functionName) {
        case 'ERROR':
            embed = createBaseEmbed(`THEMIS System Error`, COLORS.RED, `An error occurred in function: \`${data.functionName || 'Unknown'}\``, [
                { name: 'Error Message', value: `\`\`\`${data.error || 'No message provided.'}\`\`\`` },
                { name: 'Stack Trace', value: `\`\`\`${data.stack || 'No stack trace available.'}\`\`\`` }
            ]);
            break;

        case 'updateAvailable':
            embed = createBaseEmbed('THEMIS Update Available', COLORS.BLUE, "A new version of the THEMIS script has been detected. Please update at your earliest convenience by going to `Extensions > Apps Script` and pasting in the new code.", [
                { name: 'Current Version', value: `\`${data.currentVersion}\``, inline: true },
                { name: 'New Version', value: `\`${data.newVersion}\``, inline: true }
            ]);
            embed.url = 'https://github.com/wpenistone/THEMIS-DB-Sheets';
            break;

        case 'Hebe_Initiat': {
            const fields = [];
            fields.push({ name: 'Player', value: data.player, inline: true });
            fields.push({ name: 'Rank', value: data.rank, inline: true });
            fields.push({ name: 'Assigned To', value: _getDisplaySectionName(data.location), inline: true });
            if (data.discordId) fields.push({ name: 'Discord User', value: `<@${data.discordId}>`, inline: true });
            if (data.region) fields.push({ name: 'Region', value: data.region, inline: true });
            if (data.email) fields.push({ name: 'Email', value: data.email, inline: true });

            embed = createBaseEmbed('New Recruit Added', COLORS.GREEN, null, fields);
            embed.author = { name: authorString };
            break;
        }
        case 'MEMBER_UPDATE': {
            const { oldState, newState } = data;
            const updateFields = _Hephaestus_Comparat_Mutationes(oldState, newState);

            if (updateFields.length === 0) {
                Logger.log(`Skipping MEMBER_UPDATE log for ${newState.player} as no changes were detected.`);
                return;
            }

            let title, color;
            const rankChanged = oldState.rank !== newState.rank;
            const isPromotion = rankChanged && _getRankIndex(newState.rank) > _getRankIndex(oldState.rank);
            const isDemotion = rankChanged && _getRankIndex(newState.rank) < _getRankIndex(oldState.rank);

            if (isPromotion) {
                title = `Member Promoted: ${newState.player}`;
                color = COLORS.GREEN;
            } else if (isDemotion) {
                title = `Member Demoted: ${newState.player}`;
                color = COLORS.AMBER;
            } else {
                title = `Member Record Updated: ${newState.player}`;
                color = COLORS.BLUE;
            }

            embed = createBaseEmbed(title, color);
            embed.fields = updateFields;
            embed.author = { name: authorString };
            break;
        }
        case 'Atropos_Secat': {
            embed = createBaseEmbed(`Member Deleted: ${data.deletedMember.player}`, COLORS.RED);
            embed.fields = _Hades_Catalogit_Animam(data.deletedMember);
            embed.author = { name: authorString };
            break;
        }
        case 'Morpheus_Inducit': {
            const loaTitleAction = data.isUpdate ? 'LOA Updated' : 'LOA Set';
            const rawLoaId = String(data.discordId || '').replace(/\D/g, '');

            embed = createBaseEmbed(`${loaTitleAction} for ${data.player}`, COLORS.BLUE);
            embed.author = { name: authorString };

            const loaDetails = `Start Date: ${data.startDate}\n` +
                               `End Date:   ${data.endDate}\n` +
                               `Reason:     ${data.reason}` +
                               (data.isUpdate ? `\nSet By:     ${data.setBy}` : '');
            embed.fields = [{ name: 'LOA Details', value: "```\n" + loaDetails + "\n```" }];
            if (rawLoaId) {
                content = `<@${rawLoaId}>`;
            }
            break;
        }
        case 'Morpheus_Excit': {
            embed = createBaseEmbed(`LOA Ended for ${data.player}`, COLORS.AMBER);
            embed.author = { name: authorString };

            const loaDetails = (data.originalNote && data.originalNote.trim())
                ? data.originalNote.trim()
                : `Original Start: ${data.originalStartDate}\n` +
                  `Original End:   ${data.originalEndDate}\n` +
                  `Reason:         ${data.originalReason}`;

            embed.fields = [{ name: 'Original LOA Details', value: "```\n" + loaDetails + "\n```" }];
            if (data.discordId) {
                content = `<@${data.discordId}>'s LOA has ended.`;
            }
            break;
        }
        case 'Horae_Expirant': {
            const memberCount = data.expiredMembers.length;
            if (memberCount === 0) {
                return;
            }
            embed = createBaseEmbed('Daily Expired LOA Report', COLORS.AMBER);
            embed.description = `The following ${memberCount === 1 ? "member's" : "members'"} LOA has expired and their status has been automatically updated.`;

            embed.fields = data.expiredMembers.map(m => {
                const noteContent = (m.loaNote && m.loaNote.trim())
                    ? m.loaNote.trim()
                    : 'Original note details were not available.'; 

                return {
                    name: `**${m.player}** (${m.location})`,
                    value: "```\n" + noteContent + "\n```",
                    inline: false 
                };
            });

            if (THEMIS_CONFIG.LOA_MENTION_ROLE_ID && THEMIS_CONFIG.LOA_MENTION_ROLE_ID !== "your_role_id") {
                content = `<@&${THEMIS_CONFIG.LOA_MENTION_ROLE_ID}> LOA status has been updated.`;
            }
            break;
        }
        case 'Janus_Registrat': {
            embed = createBaseEmbed('Event Logged', COLORS.BLUE);
            embed.description = "```\n" + data.logContent + "\n```";
            embed.author = { name: authorString };

            break;
        }
        default:
            embed = createBaseEmbed(`THEMIS System Log: ${functionName}`, COLORS.RED);
            embed.description = `An unhandled log was triggered.`;
            embed.fields = [{ name: 'Log Details', value: "```json\n" + JSON.stringify(data, null, 2) + "\n```" }];
            break;
    }

    const payload = { embeds: [embed] };
    if (content) {
        payload.content = content;
    }

    return payload;
}

function _Charon_Accipit_Vecturam(payload) {
    const lock = LockService.getScriptLock();
    lock.waitLock(5000); 
    try {
        const cache = CacheService.getScriptCache();
        let queue = [];
        const cachedQueue = cache.get(THEMIS_CONFIG.CACHE_KEYS.WEBHOOK_QUEUE_KEY);
        if (cachedQueue) {
            try {
                queue = JSON.parse(cachedQueue);
            } catch (e) {

                Logger.log(`Webhook queue was corrupted. Starting fresh. Error: ${e.message}`);
            }
        }
        queue.push(payload);
        cache.put(THEMIS_CONFIG.CACHE_KEYS.WEBHOOK_QUEUE_KEY, JSON.stringify(queue), 21600); 
    } finally {
        lock.releaseLock();
    }
}

function Hermes_Expedit_Mandata() {
    const lock = LockService.getScriptLock();

    if (!lock.tryLock(1000)) {
        Logger.log("Skipping queue processing run; another process is active.");
        return;
    }

    try {
        const cache = CacheService.getScriptCache();
        const cachedQueue = cache.get(THEMIS_CONFIG.CACHE_KEYS.WEBHOOK_QUEUE_KEY);
        if (!cachedQueue) return;

        let queue = [];
        try {
            queue = JSON.parse(cachedQueue);
        } catch (e) {
            Logger.log(`Could not parse webhook queue. Clearing invalid data. Error: ${e.message}`);
            cache.remove(THEMIS_CONFIG.CACHE_KEYS.WEBHOOK_QUEUE_KEY);
            return;
        }

        if (queue.length === 0) return;

        const startTime = new Date().getTime();
        const timeLimit = 45 * 1000; 

        while (queue.length > 0) {

            if (new Date().getTime() - startTime > timeLimit) {
                Logger.log("Webhook processor hit time limit. Will continue on next trigger.");
                break; 
            }

            const payload = queue.shift(); 

            const success = _Iris_Volat(payload);

            if (!success) {
                Logger.log("Webhook failed to send, re-queuing for a later attempt.");
                queue.unshift(payload); 
                if (a_hasUrlFetchPermission === false) {
                    Logger.log("Permission error detected. Halting webhook processing for this run.");
                    break; 
                }
            }

            Utilities.sleep(1000); 
        }

        if (queue.length > 0) {
            cache.put(THEMIS_CONFIG.CACHE_KEYS.WEBHOOK_QUEUE_KEY, JSON.stringify(queue), 21600);
        } else {
            cache.remove(THEMIS_CONFIG.CACHE_KEYS.WEBHOOK_QUEUE_KEY);
        }

    } finally {
        lock.releaseLock();
    }
}
function _Peitho_Suadet(username, oldRank, newRank, oldLocation, newLocation) {
    const rankChanged = oldRank !== newRank;
    const locationChanged = oldLocation !== newLocation;
    const rankValueOld = _getRankIndex(oldRank);
    const rankValueNew = _getRankIndex(newRank);

    if (locationChanged && rankChanged) {
        return `Moved ${username} to ${newLocation} as ${newRank}.`;
    } else if (locationChanged) {
        return `Moved ${username} to ${newLocation}.`;
    } else if (rankChanged) {
        if (rankValueNew > rankValueOld) {
            return `Promoted ${username} to ${newRank}.`;
        } else {
            return `Demoted ${username} to ${newRank}.`;
        }
    } else {
        return `Successfully updated data for ${username}.`;
    }
}

function _formatDayForLogging(day) {
    if (!day || typeof day !== "string") {
        return "";
    }
    const trimmedDay = day.trim();
    return trimmedDay.charAt(0).toUpperCase() + trimmedDay.slice(1).toLowerCase();
}

function _formatEventTypeForLogging(eventType) {
    if (!eventType || typeof eventType !== "string") {
        return "";
    }
    const trimmedType = eventType.trim();
    if (trimmedType.length <= 2) {
        return trimmedType.toUpperCase();
    }
    return trimmedType.toLowerCase().split(" ").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
}

function getCurrentUserEmail() {
    return Session.getActiveUser().getEmail();
}

function _Delphicum_Oraculum_Consulit(email) {
    if (!email || typeof email !== 'string') {
        return null;
    }

    const lowerCaseEmail = email.toLowerCase();
    const cache = CacheService.getScriptCache();

    const userCacheKey = `${THEMIS_CONFIG.CACHE_KEYS.USER_DATA_PREFIX}${lowerCaseEmail}`;
    const cachedUser = cache.get(userCacheKey);
    if (cachedUser) {
        try { return JSON.parse(cachedUser); } catch(e) {}
    }

    const masterMapCacheKey = 'master_email_map_v1';
    const cachedMasterMap = cache.get(masterMapCacheKey);
    if (cachedMasterMap) {
        try {
            const masterMap = JSON.parse(cachedMasterMap);
            const user = masterMap[lowerCaseEmail];
            if (user) {
                cache.put(userCacheKey, JSON.stringify(user), THEMIS_CONFIG.CACHE_DURATIONS.STANDARD);
                return user;
            }
            return null; 
        } catch(e) {
        }
    }

    Logger.log(`Performing fallback to rebuild user data cache for: ${email}`);
    const allCompanymen = _Clio_Scribit_Catalogum();
    if (!allCompanymen || allCompanymen.length === 0) {
        return null; 
    }

    const newMasterMap = {};
    let foundUser = null;

    for (const person of allCompanymen) {
        if (person.email && typeof person.email === 'string') {
            const personEmailLower = person.email.toLowerCase();
            newMasterMap[personEmailLower] = person;

            if (personEmailLower === lowerCaseEmail) {
                foundUser = person;
            }
        }
    }

    if (Object.keys(newMasterMap).length > 0) {
        cache.put(masterMapCacheKey, JSON.stringify(newMasterMap), THEMIS_CONFIG.CACHE_DURATIONS.SHORT);
    }

    if (foundUser) {
        cache.put(userCacheKey, JSON.stringify(foundUser), THEMIS_CONFIG.CACHE_DURATIONS.STANDARD);
    }

    return foundUser;
}

function _Mnemosyne_Recitat() {
    const cache = CacheService.getScriptCache();
    const cacheKey = THEMIS_CONFIG.CACHE_KEYS.COMPANY;
    const cached = cache.get(cacheKey);

    if (cached) {
        try {

            const unzippedBytes = Utilities.base64Decode(cached);
            const unzippedBlob = Utilities.newBlob(unzippedBytes).setContentType('application/zip');
            const unzippedJson = Utilities.unzip(unzippedBlob)[0].getDataAsString();
            return JSON.parse(unzippedJson);
        } catch (e) {
            Logger.log(`Could not decompress/parse global company cache. Refetching. Error: ${e.message}`);

            cache.remove(cacheKey);
        }
    }

    const allCompanymen = _Clio_Scribit_Catalogum();
    const availabilityMap = _Tyche_Aestimat_Spatium(allCompanymen);

    const dataToCache = {
        companymen: allCompanymen,
        availability: availabilityMap
    };

    try {

        const jsonString = JSON.stringify(dataToCache);
        if (jsonString.length > 1000) { 
            const blob = Utilities.newBlob(jsonString, 'application/json');
            const zippedBlob = Utilities.zip([blob]);
            const zippedBase64 = Utilities.base64Encode(zippedBlob.getBytes());
            cache.put(cacheKey, zippedBase64, THEMIS_CONFIG.CACHE_DURATIONS.SHORT);
        } else {

            cache.put(cacheKey, jsonString, THEMIS_CONFIG.CACHE_DURATIONS.SHORT);
        }
    } catch(e) {

        Logger.log(`Warning: Failed to save global company cache even after compression. Error: ${e.message}`);
    }

    return dataToCache;
}

function _Lethe_Delet() {
    invalidateSheetCaches(); 

    const cache = CacheService.getScriptCache();
    const keysToRemove = [
        THEMIS_CONFIG.CACHE_KEYS.COMPANY,
        THEMIS_CONFIG.CACHE_KEYS.RECRUIT_DATA,
        THEMIS_CONFIG.CACHE_KEYS.TOTAL_SLOTS_MAP
    ];
    const userEmail = getCurrentUserEmail();
    if (userEmail) {
        const userCacheKey = `${THEMIS_CONFIG.CACHE_KEYS.USER_DATA_PREFIX}${userEmail.toLowerCase()}`;
        keysToRemove.push(userCacheKey);
    }

    cache.removeAll(keysToRemove);
    Logger.log("Invalidated global and user-specific caches.");
    return true;
}
function _invalidateAggregateCaches() {
    const cache = CacheService.getScriptCache();
    const keysToRemove = [
        THEMIS_CONFIG.CACHE_KEYS.COMPANY,
        THEMIS_CONFIG.CACHE_KEYS.RECRUIT_DATA,
        THEMIS_CONFIG.CACHE_KEYS.TOTAL_SLOTS_MAP,
        'master_email_map_v1' 
    ];

    const userEmail = getCurrentUserEmail();
    if (userEmail) {
        const userCacheKey = `${THEMIS_CONFIG.CACHE_KEYS.USER_DATA_PREFIX}${userEmail.toLowerCase()}`;
        keysToRemove.push(userCacheKey);
    }

    cache.removeAll(keysToRemove);
    Logger.log("Invalidated aggregate caches (Company, Recruit Data, User, etc.).");
}
function invalidateSheetCaches() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const allSheetNames = ss.getSheets().map(sheet => sheet.getName());
    if (allSheetNames.length === 0) return;

    const cache = CacheService.getScriptCache();
    const keysToRemove = allSheetNames.map(name => `${THEMIS_CONFIG.CACHE_KEYS.SHEET_DATA_PREFIX}${name}`);

    a_sheetDataCache = new Map();

    cache.removeAll(keysToRemove);
    Logger.log(`Invalidated ${keysToRemove.length} per-sheet caches.`);
}

function clearAllCache() {
    _Lethe_Delet();
    return "Script cache has been cleared.";
}

function Tyche_Mutat_Fortunam(sourceIdentifier, fieldsData) {
    const lock = LockService.getScriptLock();
    if (!lock.tryLock(THEMIS_CONFIG.LOCK_TIMEOUT_MS)) {
        return { status: SCRIPT_STATUS.ERROR, message: "Server is busy. Please try again." };
    }

    try {
        const ss = SpreadsheetApp.getActiveSpreadsheet();

        const oldState = _getSingleCompanyman(sourceIdentifier, ss);
        if (!oldState) throw new Error("Could not find the specified person.");

        _Nemesis_Verificat(oldState, ss);

        const config = _findNodeBySourceIdentifier(sourceIdentifier);
        if (!config) throw new Error("Could not find configuration for member.");

        const layout = _Themis_Praescribit_Legem(config);

        const sheetId = _getSheetId(ss, oldState.sheetName);
        const allRequests = [];

        for (const field of THEMIS_CONFIG.CUSTOM_FIELDS) {
            if (fieldsData.hasOwnProperty(field.key)) {
                let value = fieldsData[field.key];

                if (field.validation && field.validation.regex && typeof value === 'string') {
                    const regex = new RegExp(field.validation.regex);
                    if (!regex.test(value)) {
                        throw new Error(field.validation.regexError || `Invalid format for '${field.label}'.`);
                    }
                }

                if (field.type === 'integer') {
                    const numValue = parseInt(value, 10);
                    if (isNaN(numValue)) throw new Error(`Value for '${field.label}' must be a number.`);
                    if (field.validation) {
                        if (field.validation.min !== undefined && numValue < field.validation.min) throw new Error(`'${field.label}' must be at least ${field.validation.min}.`);
                        if (field.validation.max !== undefined && numValue > field.validation.max) throw new Error(`'${field.label}' must be no more than ${field.validation.max}.`);
                    }
                    value = numValue;
                }

                const offset = layout.offsets[field.offsetKey];
                if (offset) {
                    const userEnteredValue = (field.type === 'integer') ? { numberValue: value } : { stringValue: String(value) };
                    allRequests.push({
                        updateCells: {
                            rows: [{ values: [{ userEnteredValue }] }],
                            fields: "userEnteredValue",
                            start: {
                                sheetId: sheetId,
                                rowIndex: (oldState.row - 1) + offset.row,
                                columnIndex: (oldState.startCol - 1) + offset.col
                            }
                        }
                    });
                }
            }
        }

        if (allRequests.length > 0) {
            Sheets.Spreadsheets.batchUpdate({ requests: allRequests }, ss.getId());
            invalidateSpecificSheetCaches([oldState.sheetName]);
            updateLastModifiedTimestamp();
        }

        const newState = _getSingleCompanyman(sourceIdentifier, ss);

        Aletheia_Testatur('MEMBER_UPDATE', 'Tyche_Mutat_Fortunam', {
            user: getCurrentUserEmail(),
            oldState: oldState,
            newState: newState
        });

        return {
            status: SCRIPT_STATUS.SUCCESS,
            message: "Custom fields updated successfully.",
            updatedPerson: newState
        };

    } catch (e) {
        Aletheia_Testatur('ERROR', 'Tyche_Mutat_Fortunam', { message: e.message, stack: e.stack, user: getCurrentUserEmail() });
        return { status: SCRIPT_STATUS.ERROR, message: e.message };
    } finally {
        lock.releaseLock();
    }
}

function updateLastModifiedTimestamp() {
    PropertiesService.getScriptProperties().setProperty('lastModified', new Date().getTime().toString());
}

function Apollo_Illuminat_Eventum() {
    Hermes_Expedit_Mandata();
    const { companymen: allCompanymen } = _Mnemosyne_Recitat();
    const structure = _getStructureFromHierarchy();
    const minHostRank = THEMIS_CONFIG.LOGIC_THRESHOLDS.MIN_HOST_RANK || 'CPL';

    const minHostRankIndex = THEMIS_CONFIG.RANK_HIERARCHY.findIndex(r => r.name.toUpperCase() === minHostRank.toUpperCase());

    const ncos = minHostRankIndex === -1 ? [] : allCompanymen.filter(p => {
        const rankIndex = THEMIS_CONFIG.RANK_HIERARCHY.findIndex(r => r.name.toUpperCase() === p.rank.toUpperCase());
        return rankIndex !== -1 && rankIndex >= minHostRankIndex;
    });

    const userEmail = getCurrentUserEmail();
    const userData = _Delphicum_Oraculum_Consulit(userEmail);

    const data = {
        structure: structure,
        hierarchy: THEMIS_CONFIG.ORGANIZATION_HIERARCHY,
        eventTypes: THEMIS_CONFIG.EVENT_TYPE_DEFINITIONS.map(def => def.name),
        eventTypeDefinitions: THEMIS_CONFIG.EVENT_TYPE_DEFINITIONS,
        allCompanymen: allCompanymen,
        ncos: ncos.map(p => ({ player: p.player, rank: p.rank, location: p.location, discordId: p.discordId || null })),
        rankHierarchy: THEMIS_CONFIG.RANK_HIERARCHY,
        minHostRank: THEMIS_CONFIG.LOGIC_THRESHOLDS.MIN_HOST_RANK || 'CPL',
        validationRules: THEMIS_CONFIG.VALIDATION_RULES || {},
        dateFormat: THEMIS_CONFIG.DATE_FORMAT,
        userData: userData
    };
    return data;
}

function _getEventLogStartCoordinates(sectionPathIdentifier) {
    if (!sectionPathIdentifier) return null;

    let pathParts = sectionPathIdentifier.split('>');

    for (let i = pathParts.length; i > 0; i--) {
        const currentPathToTest = pathParts.slice(0, i).join('>');
        const result = _findNodeAndPathByPathIdentifier(currentPathToTest);

        if (result && result.node && result.node.eventLogStart) {
            return result.node.eventLogStart; 
        }
    }

    return null; 
}
function _getEventLogColumnsForSection(sectionPathIdentifier) {
    if (!sectionPathIdentifier) {
        return THEMIS_CONFIG.EVENT_LOG_COLUMNS;
    }

    const result = _findNodeAndPathByPathIdentifier(sectionPathIdentifier);

    if (result && result.node && result.node.eventLogColumns) {
        return result.node.eventLogColumns;
    }

    return THEMIS_CONFIG.EVENT_LOG_COLUMNS;
}
function Janus_Registrat(eventData) {
    try {
        let sectionName = eventData.section;
        if (sectionName) {
            const resolvedName = _resolveSectionShortcut(sectionName);
            if (resolvedName) sectionName = resolvedName;
        }
        if (!sectionName) throw new Error("A valid section or shortcut is required.");
        if (!eventData.host) throw new Error("A host is required.");
        if (!eventData.attendees || eventData.attendees.length === 0) throw new Error("At least one attendee is required.");

        const allCompanymen = _Mnemosyne_Recitat().companymen;
        const hostData = allCompanymen.find(p => p.player.toLowerCase() === eventData.host.toLowerCase());
        if (!hostData) throw new Error(`Host "${eventData.host}" was not found in the master lists.`);

        const minHostRank = THEMIS_CONFIG.LOGIC_THRESHOLDS.MIN_HOST_RANK || 'CPL';
        const minHostRankValue = _getRankIndex(minHostRank);
        const hostRankValue = _getRankIndex(hostData.rank);
        if (minHostRankValue !== -1 && (hostRankValue === -1 || hostRankValue < minHostRankValue)) {
            throw new Error(`Host must be the rank of ${minHostRank} or higher. ${hostData.player} is a ${hostData.rank}.`);
        }

        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const spreadsheetId = ss.getId();
        const allRequests = [];
        const eventLogForDiscord = `Event Type:  ${eventData.eventType}\n` +
            `Section:     ${_getDisplaySectionName(sectionName)}\n` +
            `Day:         ${eventData.day}\n` +
            `Host:        ${eventData.host}\n` +
            `Description: ${eventData.description || 'N/A'}\n` +
            `Attendees:   (${eventData.attendees.length}) ${eventData.attendees.join(', ')}`;

        const eventLogSheetName = THEMIS_CONFIG.EVENT_LOG_SHEET_NAME;
        if (!eventLogSheetName) throw new Error("Config key 'EVENT_LOG_SHEET_NAME' is not defined.");
        const eventLogSheet = ss.getSheetByName(eventLogSheetName);
        if (!eventLogSheet) throw new Error(`Sheet "${eventLogSheetName}" not found.`);

        let startCoords = _getEventLogStartCoordinates(sectionName);
        if (!startCoords) {
             const topLevelNode = THEMIS_CONFIG.ORGANIZATION_HIERARCHY.find(node => node.eventLogStart);
             if (topLevelNode) startCoords = topLevelNode.eventLogStart;
        }
        if (!startCoords) throw new Error("No event Aletheia_Testatur start position is defined in the configuration.");

        const startCol = startCoords.col;
        const sectionColIndex = startCol + THEMIS_CONFIG.EVENT_LOG_COLUMNS.SECTION;
        const lastRowInSheet = eventLogSheet.getLastRow();
        let targetRow;

        if (lastRowInSheet < startCoords.row) {
            targetRow = startCoords.row;
        } else {
            const values = eventLogSheet.getRange(startCoords.row, sectionColIndex, lastRowInSheet - startCoords.row + 1, 1).getValues();
            const emptyIndex = values.findIndex(row => !row[0] || row[0].toString().trim() === '');
            targetRow = (emptyIndex !== -1) ? startCoords.row + emptyIndex : lastRowInSheet + 1;
        }

        const cols = _getEventLogColumnsForSection(sectionName);
        const maxCol = Math.max(...Object.values(cols));
        const eventLogValues = new Array(maxCol + 1).fill({});

        const sectionNameForLog = _getSectionNameForLogging(sectionName);
        eventLogValues[cols.SECTION] = { userEnteredValue: { stringValue: sectionNameForLog }};

        eventLogValues[cols.DAY] = { userEnteredValue: { stringValue: eventData.day }};
        eventLogValues[cols.HOST] = { userEnteredValue: { stringValue: eventData.host }};
        eventLogValues[cols.TYPE] = { userEnteredValue: { stringValue: eventData.eventType }, note: eventLogForDiscord };

        allRequests.push({ updateCells: { rows: [{ values: eventLogValues }], fields: "userEnteredValue,note", start: { sheetId: eventLogSheet.getSheetId(), rowIndex: targetRow - 1, columnIndex: startCol - 1 } }});

        const attendanceSheetName = THEMIS_CONFIG.ATTENDANCE_SHEET_NAME;
        if (!attendanceSheetName) throw new Error("Config key 'ATTENDANCE_SHEET_NAME' is not defined.");
        const attendanceSheet = ss.getSheetByName(attendanceSheetName);
        if (!attendanceSheet) throw new Error(`Sheet "${attendanceSheetName}" not found.`);

        const targetColumn = THEMIS_CONFIG.ATTENDANCE_DAY_COLUMNS[eventData.day];
        if (!targetColumn) throw new Error(`No column mapping found for day "${eventData.day}".`);

        const columnValues = attendanceSheet.getRange(1, targetColumn, attendanceSheet.getMaxRows(), 1).getValues();
        let lastRowWithData = 0;
        for (let i = columnValues.length - 1; i >= 0; i--) {
            if (columnValues[i][0] && columnValues[i][0].toString().trim() !== "") {
                lastRowWithData = i + 1;
                break;
            }
        }

        const attendanceStartRow = Math.max(lastRowWithData + 2, THEMIS_CONFIG.ATTENDANCE_DATA_START_ROW);

        const uniqueAttendees = [...new Set(eventData.attendees)];

        const endRowLimit = THEMIS_CONFIG.ATTENDANCE_DATA_END_ROW;
        if (endRowLimit && (attendanceStartRow + uniqueAttendees.length - 1 > endRowLimit)) {
            throw new Error(`Not enough space to Aletheia_Testatur attendance. The designated area (up to row ${endRowLimit}) is full.`);
        }

        const attendanceRows = uniqueAttendees.map(attendee => ({ values: [{ userEnteredValue: { stringValue: attendee } }] }));
        allRequests.push({ updateCells: { rows: attendanceRows, fields: "userEnteredValue", start: { sheetId: attendanceSheet.getSheetId(), rowIndex: attendanceStartRow - 1, columnIndex: targetColumn - 1 } }});

        if (allRequests.length > 0) {
            Sheets.Spreadsheets.batchUpdate({ requests: allRequests }, spreadsheetId);
        }

        Aletheia_Testatur('Janus_Registrat', 'N/A', { user: getCurrentUserEmail(), logContent: eventLogForDiscord });
        return { status: SCRIPT_STATUS.SUCCESS, message: "Event and attendance logged successfully!" };

    } catch (e) {
        Aletheia_Testatur('ERROR', 'Janus_Registrat', { message: e.message, stack: e.stack, user: getCurrentUserEmail() });
        return { status: SCRIPT_STATUS.ERROR, message: e.message };
    }
}

function getPersonFromIdentifier(identifier) {
    if (!identifier) return null;
    const allCompanymen = _Mnemosyne_Recitat().companymen;
    return allCompanymen.find(p => p.sourceIdentifier === identifier) || null;
}

function getLoaCheckboxCell(person, ss) {
    const sheet = ss.getSheetByName(person.sheetName);
    if (!sheet) {
        throw new Error(`Sheet "${person.sheetName}" not found for ${person.player}.`);
    }

    const layoutName = person.layoutName;
    if (!layoutName) {
        throw new Error(`Layout information is missing for ${person.player}. The spreadsheet cache might be outdated.`);
    }

    const layout = THEMIS_CONFIG.LAYOUT_BLUEPRINTS[layoutName];
    if (!layout || !layout.offsets || !layout.offsets.LOAcheckbox) {
        throw new Error(`"LOAcheckbox" offset not defined in the "${layoutName}" blueprint.`);
    }

    const checkboxOffset = layout.offsets.LOAcheckbox;

    const targetRow = person.row + checkboxOffset.row;
    const targetCol = person.startCol + checkboxOffset.col;

    return sheet.getRange(targetRow, targetCol);
}

function Apollo_Illuminat_Concilium() {
    Hermes_Expedit_Mandata();
    const { companymen, availability } = _Mnemosyne_Recitat();
    const structure = _getStructureFromHierarchy();
    const allLocations = Object.keys(_getTotalSlotsMap());
    const userEmail = getCurrentUserEmail();
    const userData = _Delphicum_Oraculum_Consulit(userEmail);

    if (!userData) {
        SpreadsheetApp.getActiveSpreadsheet().toast(
            `User profile (${userEmail}) not found. Some features may be limited.`,
            'THEMIS Notice',
            8
        );
    }

    const clientCompanymen = companymen.map(p => {
        const rankInfo = THEMIS_CONFIG.RANK_HIERARCHY.find(r => r.name === p.rank);
        return {
            player: p.player, rank: p.rank, rankAbbr: rankInfo ? rankInfo.abbr : null,
            location: p.location, locationPath: p.locationPath, joinDate: p.joinDate,
            onLOA: p.onLOA, loaData: p.loaData, sourceIdentifier: p.sourceIdentifier,
            blueprint: p.blueprint, rankKey: p.rankKey, email: p.email,
            sheetName: p.sheetName, row: p.row, startCol: p.startCol,
            customFields: p.customFields || {} 
        };
    });

    return {
        companymen: clientCompanymen,
        structure: structure,
        hierarchy: THEMIS_CONFIG.ORGANIZATION_HIERARCHY,
        totalSlotsMap: _getTotalSlotsMap(),
        availabilityMap: availability,
        rankHierarchy: THEMIS_CONFIG.RANK_HIERARCHY,
        allLocations: allLocations,
        timeInRankRequirements: THEMIS_CONFIG.TIME_IN_RANK_REQUIREMENTS, 
        ubtSettings: THEMIS_CONFIG.UBT_SETTINGS,
        emailRequirement: THEMIS_CONFIG.LOGIC_THRESHOLDS.EMAIL_REQUIRED_MIN_RANK,
        customFieldsConfig: THEMIS_CONFIG.CUSTOM_FIELDS,
        customFieldsUiEditable: THEMIS_CONFIG.CUSTOM_FIELDS_UI_EDITABLE,
        validationRules: THEMIS_CONFIG.VALIDATION_RULES || {},
        sheetAccessConfig: THEMIS_CONFIG.SHEET_ACCESS_MANAGEMENT,
        userData: userData 
    };
}

function _getTotalSlotsMap() {
    const cache = CacheService.getScriptCache();
    const cacheKey = THEMIS_CONFIG.CACHE_KEYS.TOTAL_SLOTS_MAP;
    const cached = cache.get(cacheKey);
    if (cached) {
        return JSON.parse(cached);
    }

    const totalSlots = {};

    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node, path) => {
        const currentPath = path.map(n => n.name).join('>');
        if (!totalSlots[currentPath]) {
            totalSlots[currentPath] = { _titledSlots: {} };
        }

        let slotsToProcess = [];
        const blueprintName = node.useSlotsFrom;
        if (blueprintName && THEMIS_CONFIG.SLOT_BLUEPRINTS[blueprintName]) {
            slotsToProcess = THEMIS_CONFIG.SLOT_BLUEPRINTS[blueprintName];
        } else if (node.slots) {
            slotsToProcess = node.slots;
        }

        for (const slot of slotsToProcess) {
            const allRanks = slot.ranks || (slot.rank ? [slot.rank] : []);
            const count = slot.count || (slot.location?.rows?.length) || (slot.locations?.length) || (slot.location?.endRow - slot.location?.startRow + 1) || 1;

            allRanks.forEach(rank => {
                const rankUpper = rank.toUpperCase();
                if (slot.title) {
                    if (!totalSlots[currentPath]._titledSlots[rankUpper]) {
                        totalSlots[currentPath]._titledSlots[rankUpper] = {};
                    }
                    totalSlots[currentPath]._titledSlots[rankUpper][slot.title] = (totalSlots[currentPath]._titledSlots[rankUpper][slot.title] || 0) + count;
                } else {
                    totalSlots[currentPath][rankUpper] = (totalSlots[currentPath][rankUpper] || 0) + count;
                }
            });
        }
    });

    cache.put(cacheKey, JSON.stringify(totalSlots), 21600);
    return totalSlots;
}

function _findNodeBySourceIdentifier(sourceIdentifier) {
    const { sourceIdToConfig } = _getConfigIndexes();
    return sourceIdToConfig.get(sourceIdentifier) || null;
}

function _getSingleCompanyman(sourceIdentifier, ss) {
    const config = _findNodeBySourceIdentifier(sourceIdentifier);
    if (!config) return null;

    const [sheetName, rowStr, colStr] = sourceIdentifier.split('|');
    const row = parseInt(rowStr);
    const col = parseInt(colStr);

    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) return null;

    const { node, slot, path, fullPath } = config; 

    const layoutName = slot.layout || _Maia_Investigat_Progeniem(fullPath, 'layout'); 
    const layout = THEMIS_CONFIG.LAYOUT_BLUEPRINTS[layoutName];
    if (!layout) return null;

    const offsets = layout.offsets;

    let minRowOffset = 0, maxRowOffset = 0, minColOffset = 0, maxColOffset = 0;
    const allOffsetKeys = [...new Set([
        ...Object.keys(offsets),
        ...(THEMIS_CONFIG.CUSTOM_FIELDS || []).map(f => f.offsetKey)
    ])];

    allOffsetKeys.forEach(key => {
        const offset = offsets[key];
        if (offset) {
            minRowOffset = Math.min(minRowOffset, offset.row);
            maxRowOffset = Math.max(maxRowOffset, offset.row);
            minColOffset = Math.min(minColOffset, offset.col);
            maxColOffset = Math.max(maxColOffset, offset.col);
        }
    });

    const startRow = row + minRowOffset;
    const startCol = col + minColOffset;
    const numRows = (maxRowOffset - minRowOffset) + 1;
    const numCols = (maxColOffset - minColOffset) + 1;

    const dataRange = sheet.getRange(startRow, startCol, numRows, numCols);
    const values = dataRange.getValues();
    const notes = dataRange.getNotes();
    const checkedStatuses = dataRange.isChecked(); 

    const readFromCache = (offsetKey, dataType = 'values') => {
        if (!offsets[offsetKey]) return null;

        const r = offsets[offsetKey].row - minRowOffset;
        const c = offsets[offsetKey].col - minColOffset;

        if (r < 0 || r >= numRows || c < 0 || c >= numCols) return null;

        switch(dataType) {
         case 'notes':
             return (notes && notes[r] != null && notes[r][c] !== undefined) ? notes[r][c] : null;
         case 'checked':
             return (checkedStatuses && checkedStatuses[r] != null && checkedStatuses[r][c] !== undefined) ? checkedStatuses[r][c] : null;
         default:
             return (values && values[r] != null && values[r][c] !== undefined) ? values[r][c] : null;
        }
    };

    const person = {
        player: readFromCache('username'),
        location: node.name,
        locationPath: path,
        sheetName: sheetName,
        row: row,
        startCol: col,
        sourceIdentifier: sourceIdentifier,
        isHQ: layoutName === 'BILLET_OFFSETS',
        rankKey: layoutName === 'BILLET_OFFSETS' ? slot.title : null,
        customFields: {}
    };

    if (person.isHQ) {
        person.rank = slot.rank;
    } else {
        const rankOnSheet = (readFromCache('rank') || '').toString().trim().toUpperCase();
        const rankObj = THEMIS_CONFIG.RANK_HIERARCHY.find(r => (r.abbr && r.abbr.toUpperCase() === rankOnSheet) || r.name.toUpperCase() === rankOnSheet);
        person.rank = rankObj ? rankObj.name : 'Unknown';
    }

    const loaNote = readFromCache('LOAcheckbox', 'notes');
    person.onLOA = readFromCache('LOAcheckbox', 'checked');
    person.loaNote = loaNote;
    person.loaData = _parseLoaNote(loaNote);

    person.hasPassedUBT = readFromCache('BTcheckbox', 'checked');

    const joinDateValue = readFromCache('joinDate');
    const parsedDate = joinDateValue instanceof Date ? joinDateValue : _Chronos_Interpretatur(joinDateValue);
    person.joinDate = parsedDate ? Utilities.formatDate(parsedDate, Session.getScriptTimeZone(), "yyyy-MM-dd") : null;
    person.email = _Hermes_Interpretatur_Notam(readFromCache('username', 'notes'));

    person.discordId = String(readFromCache('discordId') || '').replace(/\D/g, '');
    person.region = (readFromCache('region') || '').toString().trim();

    if (THEMIS_CONFIG.CUSTOM_FIELDS) {
        THEMIS_CONFIG.CUSTOM_FIELDS.forEach(field => {
            if (offsets[field.offsetKey]) {
                const customData = {
                    value: readFromCache(field.offsetKey),
                    note: field.transferNote ? readFromCache(field.offsetKey, 'notes') : null
                };
                if (customData.value) {
                     person.customFields[field.key] = customData;
                }
            }
        });
    }

    return person;
}

function _Tyche_Aestimat_Spatium(allCompanymen) {
    const totalSlotsMap = _getTotalSlotsMap();
    const occupiedSlotsMap = {};
    allCompanymen.forEach(p => {
        const path = p.locationPath;
        const rankUpper = p.rank.toUpperCase();
        if (!path) return;

        if (!occupiedSlotsMap[path]) {
            occupiedSlotsMap[path] = { _titledSlots: {} };
        }

        if (p.rankKey) { 
            if (!occupiedSlotsMap[path]._titledSlots[rankUpper]) {
                occupiedSlotsMap[path]._titledSlots[rankUpper] = {};
            }
            occupiedSlotsMap[path]._titledSlots[rankUpper][p.rankKey] = (occupiedSlotsMap[path]._titledSlots[rankUpper][p.rankKey] || 0) + 1;
        } else {
            occupiedSlotsMap[path][rankUpper] = (occupiedSlotsMap[path][rankUpper] || 0) + 1;
        }
    });

    const availabilityMap = JSON.parse(JSON.stringify(totalSlotsMap)); 

    for (const locationPath in availabilityMap) {
        const totalLocationSlots = availabilityMap[locationPath];
        const occupiedLocationSlots = occupiedSlotsMap[locationPath];

        if (occupiedLocationSlots) {
            for (const rankUpper in totalLocationSlots) {
                if (rankUpper !== '_titledSlots' && occupiedLocationSlots[rankUpper]) {
                    totalLocationSlots[rankUpper] -= occupiedLocationSlots[rankUpper];
                }
            }

            if (totalLocationSlots._titledSlots && occupiedLocationSlots._titledSlots) {
                for (const rankUpper in totalLocationSlots._titledSlots) {
                    if (occupiedLocationSlots._titledSlots[rankUpper]) {
                        for (const title in totalLocationSlots._titledSlots[rankUpper]) {
                            if (occupiedLocationSlots._titledSlots[rankUpper][title]) {
                                totalLocationSlots._titledSlots[rankUpper][title] -= occupiedLocationSlots._titledSlots[rankUpper][title];
                            }
                        }
                    }
                }
            }
        }
    }

    return availabilityMap;
}

function findSheetNameForNode(nodeName) {
    let sheetName = null;

    _Hestia_Visit_Domos(THEMIS_CONFIG.ORGANIZATION_HIERARCHY, (node, path) => {
        if (sheetName) return;
        const parentNode = path.length > 1 ? path[path.length - 2] : null;
        const currentSheet = node.sheetName || parentNode?.sheetName;
        if (node.name === nodeName) {
            sheetName = currentSheet;
        }
    });

    return sheetName;
}

function Apollo_Illuminat_Dilectum() {
    Hermes_Expedit_Mandata(); 
    const cache = CacheService.getScriptCache();
    const cacheKey = THEMIS_CONFIG.CACHE_KEYS.RECRUIT_DATA;
    const cached = cache.get(cacheKey);
    if (cached) {
        try {
            return JSON.parse(cached);
        } catch (e) {}
    }

    const { companymen, availability } = _Mnemosyne_Recitat(); 

    const recruitRanks = THEMIS_CONFIG.RANK_HIERARCHY;
    const minRankIndex = THEMIS_CONFIG.RANK_HIERARCHY.findIndex(r => r.name === THEMIS_CONFIG.RECRUITER_MIN_RANK);

    const recruiters = companymen
        .filter(p => {
            const pRankIndex = THEMIS_CONFIG.RANK_HIERARCHY.findIndex(r => r.name === p.rank);
            return pRankIndex !== -1 && minRankIndex !== -1 && pRankIndex >= minRankIndex;
        })
        .map(p => ({
            player: p.player,
            location: p.location
        }))
        .filter(obj => obj.player)
        .sort((a, b) => a.player.localeCompare(b.player));

    const allDiscordIds = companymen
        .map(p => p.discordId ? p.discordId.replace(/\D/g, '') : null)
        .filter(Boolean);

    const userEmail = getCurrentUserEmail();
    const userData = _Delphicum_Oraculum_Consulit(userEmail);

    const data = {
        structure: _getStructureFromHierarchy(),
        hierarchy: THEMIS_CONFIG.ORGANIZATION_HIERARCHY,
        regions: THEMIS_CONFIG.REGIONS,
        ranks: recruitRanks,
        recruiters: recruiters,
        allCompanymen: companymen.map(p => p.player.toLowerCase()),
        allDiscordIds: allDiscordIds,
        availabilityMap: availability,
        totalSlotsMap: _getTotalSlotsMap(),
        allLocations: Object.keys(_getStructureFromHierarchy().groups).flatMap(groupName => _getStructureFromHierarchy().groups[groupName]),
        timeInRankRequirements: THEMIS_CONFIG.TIME_IN_RANK_REQUIREMENTS,
        emailRequirement: THEMIS_CONFIG.LOGIC_THRESHOLDS.EMAIL_REQUIRED_MIN_RANK,
        customFieldsConfig: THEMIS_CONFIG.CUSTOM_FIELDS || [],
        customFieldsUiEditable: THEMIS_CONFIG.CUSTOM_FIELDS_UI_EDITABLE || false,
        validationRules: THEMIS_CONFIG.VALIDATION_RULES || {},
        sheetAccessConfig: THEMIS_CONFIG.SHEET_ACCESS_MANAGEMENT,
        userData: userData 
    };

    cache.put(cacheKey, JSON.stringify(data), THEMIS_CONFIG.CACHE_DURATIONS.SHORT);
    return data;
}

function Argus_Panoptes_Observat(query) {
    if (!query || typeof query !== 'string') {
        return { status: SCRIPT_STATUS.ERROR, message: "Search query must be a non-empty string." };
    }
    const lowerCaseQuery = query.toLowerCase();
    const { companymen: allCompanymen } = _Mnemosyne_Recitat();

    const matchingMembers = allCompanymen.filter(member => {
        return member.player.toLowerCase().includes(lowerCaseQuery) ||
               member.rank.toLowerCase().includes(lowerCaseQuery) ||
               member.location.toLowerCase().includes(lowerCaseQuery);
    });

    if (matchingMembers.length === 0) {
        return { status: SCRIPT_STATUS.SUCCESS, message: "No members found matching your query.", results: [] };
    }

    return { status: SCRIPT_STATUS.SUCCESS, message: `${matchingMembers.length} members found.`, results: matchingMembers };
}
function Clio_Refert_Historiam() {
    const remoteVersionUrl = "https://raw.githubusercontent.com/wpenistone/THEMIS-DB-Sheets/main/v";
    let statusMessage = "";
    let statusClass = "";
    let statusTooltip = "";
    let latestVersion = "";

    try {
        const response = UrlFetchApp.fetch(remoteVersionUrl, { muteHttpExceptions: true });
        const responseCode = response.getResponseCode();

        if (responseCode === 200) {
            latestVersion = response.getContentText().trim();

            if (VERSION === latestVersion) {
                statusMessage = "You are on the latest version.";
                statusClass = "success";
                statusTooltip = `Current: ${VERSION}\nLatest: ${latestVersion}`;
            } else {
                statusMessage = "A new version is available!";
                statusClass = "warning";
                statusTooltip = `Current: ${VERSION}\nLatest: ${latestVersion}`;

                try {
                    const scriptProperties = PropertiesService.getScriptProperties();
                    const lastNotified = scriptProperties.getProperty('lastNotifiedVersion');

                    if (latestVersion !== lastNotified) {
                        const logData = {
                            currentVersion: VERSION,
                            newVersion: latestVersion,
                            authorName: 'THEMIS System' 
                        };
                        const payload = _Iris_Format_Nuntium('updateAvailable', logData);
                        if (payload) {
                            _Charon_Accipit_Vecturam(payload);
                            scriptProperties.setProperty('lastNotifiedVersion', latestVersion);
                            Logger.log(`Update notification enqueued for version ${latestVersion}.`);
                        }
                    }
                } catch (e) {
                    Logger.log(`Failed to process update notification webhook. Error: ${e.message}`);
                }
            }
        } else {
            statusMessage = "Could not verify version.";
            statusClass = "warning";
            statusTooltip = `Could not fetch the latest version information. Response code: ${responseCode}`;
        }
    } catch (e) {
        statusMessage = "Error checking for updates.";
        statusClass = "error";
        statusTooltip = e.message;
        Aletheia_Testatur('ERROR', 'Clio_Refert_Historiam', { message: e.message, stack: e.stack });
    }

    return {
        currentVersion: VERSION,
        latestVersion: latestVersion,
        statusMessage: statusMessage,
        statusClass: statusClass,
        statusTooltip: statusTooltip
    };
}

function Chronos_Indicat() {
    return VERSION;
}
function getCompanymenNameSet() {
    const cache = CacheService.getScriptCache();
    const cacheKey = 'companymen_name_set_v1'; 
    const cached = cache.get(cacheKey);

    if (cached) {
        try {
            return new Set(JSON.parse(cached));
        } catch (e) {
        }
    }

    const { companymen } = _Mnemosyne_Recitat();
    if (!companymen) {
        return new Set(); 
    }

    const namesArray = companymen.map(p => p.player.toString().trim().toLowerCase());

    cache.put(cacheKey, JSON.stringify(namesArray), THEMIS_CONFIG.CACHE_DURATIONS.SHORT);

    return new Set(namesArray);
}
function _Rhadamanthus_Inspectat_Nomina() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    ss.toast("Validation running...", "Status", 15);

    try {
        const attendanceSheet = ss.getSheetByName(THEMIS_CONFIG.ATTENDANCE_SHEET_NAME);
        if (!attendanceSheet) {
            throw new Error(`Sheet "${THEMIS_CONFIG.ATTENDANCE_SHEET_NAME}" not found.`);
        }

        const dayColumns = Object.values(THEMIS_CONFIG.ATTENDANCE_DAY_COLUMNS);
        if (dayColumns.length === 0) {
            return { status: SCRIPT_STATUS.SUCCESS, message: "No attendance columns defined in config.", invalidNames: [] };
        }
        const startCol = Math.min(...dayColumns);
        const endCol = Math.max(...dayColumns);
        const startRow = THEMIS_CONFIG.ATTENDANCE_DATA_START_ROW;
        const endRow = THEMIS_CONFIG.ATTENDANCE_DATA_END_ROW;

        const dynamicRangeString = `${_columnToLetter(startCol)}${startRow}:${_columnToLetter(endCol)}${endRow}`;
        const validationRange = attendanceSheet.getRange(dynamicRangeString);

        const attendeeNames = [...new Set(validationRange.getValues().flat().filter(Boolean).map(name => name.toString().trim()))].sort();

        if (attendeeNames.length === 0) {
            return {
                status: SCRIPT_STATUS.SUCCESS,
                message: "No attendee names found to validate.",
                invalidNames: []
            };
        }

        const masterNamesLowerCase = getCompanymenNameSet();
        if (masterNamesLowerCase.size === 0) {
            throw new Error("Could not read any names from the master lists.");
        }

        const invalidNames = attendeeNames.filter(name => !masterNamesLowerCase.has(name.toString().trim().toLowerCase()));

        return {
            status: SCRIPT_STATUS.SUCCESS,
            message: "Validation complete.",
            invalidNames: invalidNames
        };

    } catch (e) {
        Aletheia_Testatur('ERROR', '_Rhadamanthus_Inspectat_Nomina', `Validation Error: ${e.message}\n${e.stack || ""}`);
        return {
            status: SCRIPT_STATUS.ERROR,
            message: e.message
        };
    } finally {
        ss.toast("Validation finished.", "Status", 5);
    }
}

function Morpheus_Inducit(sourceIdentifier, startDate, endDate, reason) {
    try {
        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const source = getPersonFromIdentifier(sourceIdentifier);

        _Nemesis_Verificat(source, ss);

        if (!source) return { status: SCRIPT_STATUS.ERROR, message: "Could not find the specified person. Please refresh." };

        const userEmail = getCurrentUserEmail();
        const manager = _Delphicum_Oraculum_Consulit(userEmail);
        const managerName = (manager && manager.player) ? manager.player : userEmail;

        const startDateObj = new Date(startDate + 'T00:00:00');
        const endDateObj = new Date(endDate + 'T00:00:00');

        const formattedStartDate = getFormattedDateString(startDateObj);
        const formattedEndDate = getFormattedDateString(endDateObj);

        const noteContent = `Start Date: ${formattedStartDate}\nEnd Date: ${formattedEndDate}\nReason: ${reason}\n\u200B\nBy: ${managerName}`;

        const loaCheckboxCell = getLoaCheckboxCell(source, ss);
        const sheetId = loaCheckboxCell.getSheet().getSheetId();

        const request = {
            updateCells: {
                rows: [{ values: [{ userEnteredValue: { boolValue: true }, note: noteContent }] }],
                fields: "userEnteredValue,note",
                start: { sheetId: sheetId, rowIndex: loaCheckboxCell.getRow() - 1, columnIndex: loaCheckboxCell.getColumn() - 1 }
            }
        };
        Sheets.Spreadsheets.batchUpdate({ requests: [request] }, ss.getId());
        invalidateSpecificSheetCaches([source.sheetName]);
        updateLastModifiedTimestamp();

        _Lethe_Delet();
        const updatedPerson = _getSingleCompanyman(sourceIdentifier, ss);
        const { availability: newAvailabilityMap } = _Mnemosyne_Recitat();

        Aletheia_Testatur('Morpheus_Inducit', 'Morpheus_Inducit', {
            user: getCurrentUserEmail(),
            player: source.player,
            discordId: source.discordId,
            startDate: formattedStartDate,
            endDate: formattedEndDate,
            reason: reason,
            setBy: managerName,
            isUpdate: source.onLOA
        });

        return {
            status: SCRIPT_STATUS.SUCCESS,
            message: `Successfully set LOA for ${source.player}.`,
            deltaPayload: {
                updatedPersons: [updatedPerson],
                newAvailabilityMap: newAvailabilityMap
            }
        };
    } catch (e) {
        Aletheia_Testatur('ERROR', 'Morpheus_Inducit', { message: e.message, stack: e.stack, user: getCurrentUserEmail() });
        return { status: SCRIPT_STATUS.ERROR, message: e.message };
    }
}

function Morpheus_Excit(sourceIdentifier) {
    const lock = LockService.getScriptLock();
    if (!lock.tryLock(THEMIS_CONFIG.LOCK_TIMEOUT_MS)) throw new Error("Busy. Please try again shortly.");

    try {
        const source = getPersonFromIdentifier(sourceIdentifier);

        _Nemesis_Verificat(source, SpreadsheetApp.getActiveSpreadsheet());

        if (!source) return { status: SCRIPT_STATUS.ERROR, message: "Could not find the specified person. They may have been moved or deleted. Please refresh." };

        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const loaCheckboxCell = getLoaCheckboxCell(source, ss);
        const sheetId = loaCheckboxCell.getSheet().getSheetId();

        const request = {
            updateCells: {
                rows: [{ values: [{ userEnteredValue: { boolValue: false }, note: "" }] }],
                fields: "userEnteredValue,note",
                start: { sheetId: sheetId, rowIndex: loaCheckboxCell.getRow() - 1, columnIndex: loaCheckboxCell.getColumn() - 1 }
            }
        };
        Sheets.Spreadsheets.batchUpdate({ requests: [request] }, ss.getId());
        invalidateSpecificSheetCaches([source.sheetName]);
        updateLastModifiedTimestamp();

        _Lethe_Delet();
        const updatedPerson = _getSingleCompanyman(sourceIdentifier, SpreadsheetApp.getActiveSpreadsheet());
        const { availability: newAvailabilityMap } = _Mnemosyne_Recitat();

        Aletheia_Testatur('Morpheus_Excit', 'Morpheus_Excit', {
            user: getCurrentUserEmail(),
            player: source.player,
            discordId: source.discordId,
            originalStartDate: source.loaData?.startDate || 'N/A',
            originalEndDate: source.loaData?.endDate || 'N/A',
            originalReason: source.loaData?.reason || 'Not specified'
        });

        return {
            status: SCRIPT_STATUS.SUCCESS,
            message: `Successfully ended LOA for ${source.player}.`,
            deltaPayload: {
                updatedPersons: [updatedPerson],
                newAvailabilityMap: newAvailabilityMap
            }
        };
    } catch (e) {
        Aletheia_Testatur('ERROR', 'Morpheus_Excit', { message: e.message, stack: e.stack, user: getCurrentUserEmail() });
        return { status: SCRIPT_STATUS.ERROR, message: e.message };
    } finally {
        lock.releaseLock();
    }
}

function Horae_Expirant() {
    const allCompanymen = _Mnemosyne_Recitat().companymen;
    const expiredLoas = [];
    const requests = [];
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const spreadsheetId = ss.getId();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    allCompanymen.forEach(person => {
        try {
            if (person.onLOA && person.loaData && person.loaData.endDate) {
                const endDate = _Chronos_Interpretatur(person.loaData.endDate);
                if (!endDate) {
                    Aletheia_Testatur('ERROR', 'Horae_Expirant', {
                        message: `Invalid LOA end date found for ${person.player}. The date '${person.loaData.endDate}' could not be parsed. Skipping expiration for this member.`,
                        player: person.player,
                        loaNote: person.loaNote
                    });
                    return;
                }

                endDate.setHours(0, 0, 0, 0);
                if (endDate < today) {
                    expiredLoas.push(person);
                    const loaCheckboxCell = getLoaCheckboxCell(person, ss);
                    const sheetId = _getSheetId(ss, person.sheetName);

                    requests.push({
                        updateCells: {
                            rows: [{ values: [{ userEnteredValue: { boolValue: false }, note: "" }] }],
                            fields: "userEnteredValue,note",
                            start: { sheetId: sheetId, rowIndex: loaCheckboxCell.getRow() - 1, columnIndex: loaCheckboxCell.getColumn() - 1 }
                        }
                    });
                }
            }
        } catch (e) {
            Aletheia_Testatur('ERROR', 'Horae_Expirant (Loop)', `Failed to process expiration for ${person.player}. Error: ${e.message}`);
        }
    });

    if (requests.length > 0) {
        Sheets.Spreadsheets.batchUpdate({ requests: requests }, spreadsheetId);

        const expiredMembersDetails = expiredLoas.map(p => ({
            player: p.player,
            location: p.location,
            endDate: p.loaData.endDate,
            loaNote: p.loaNote || 'Note not found.' 
        }));

        if (expiredMembersDetails.length > 0) {
            Aletheia_Testatur('Horae_Expirant', 'N/A', { expiredMembers: expiredMembersDetails });
        }

        const affectedSheetNames = [...new Set(expiredLoas.map(p => p.sheetName))];
        invalidateSpecificSheetCaches(affectedSheetNames);
        updateLastModifiedTimestamp();
    }
}

function _Dike_Ordinat_Socios(members) {
    if (!members || !Array.isArray(members)) return [];

    return [...members].sort((a, b) => {

        const rankA = _getRankIndex(a.rank);
        const rankB = _getRankIndex(b.rank);
        if (rankA !== rankB) return rankB - rankA;

        const dateA = a.joinDate ? new Date(a.joinDate) : new Date(0);
        const dateB = b.joinDate ? new Date(b.joinDate) : new Date(0);
        return dateA - dateB;
    });
}

function Hebe_Initiat(details, bypassConfirmation = false, grantAccess = false) {
    const lock = LockService.getScriptLock();
    if (!lock.tryLock(THEMIS_CONFIG.LOCK_TIMEOUT_MS)) {
        throw new Error("Busy. Please try again shortly.");
    }

    try {
        const { playerName: rawPlayerName, discordId: rawDiscordId, rank, region, squad, recruiter, note, email, rankTitle, customFields } = details;

        if (grantAccess && email) {
            try {
                SpreadsheetApp.getActiveSpreadsheet().addEditor(email);
            } catch (e) {
                Aletheia_Testatur('ERROR', 'Hebe_Initiat_addEditor', { message: `Failed to grant editor access to ${email}. Error: ${e.message}`, user: getCurrentUserEmail() });
            }
        }

        let ubtStatus = false;
        const triggerRank = THEMIS_CONFIG.UBT_SETTINGS.TRIGGER_RANK;
        if (triggerRank) {
            const recruitRankIndex = _getRankIndex(rank);
            const triggerRankIndex = _getRankIndex(triggerRank);

            if (recruitRankIndex >= triggerRankIndex && !bypassConfirmation) {
                const ubtName = THEMIS_CONFIG.UBT_SETTINGS.NAME || 'Training';
                const promptTemplate = THEMIS_CONFIG.UBT_SETTINGS.PROMPT_MESSAGE || 'This recruitment rank requires the member to have passed {name}. Is this correct?';
                return { status: SCRIPT_STATUS.NEEDS_CONFIRMATION, message: promptTemplate.replace('{name}', ubtName) };
            }
            if (bypassConfirmation) ubtStatus = true;
        }

        const playerName = rawPlayerName.trim();
        const discordId = rawDiscordId.replace(/\D/g, '');
        const formattedJoinDate = getFormattedDateString(new Date());
        const { companymen: allCompanymen } = _Mnemosyne_Recitat();

        if (allCompanymen.some(p => p.player.toLowerCase() === playerName.toLowerCase())) {
            return { status: SCRIPT_STATUS.ERROR, message: `Player "${playerName}" already exists in the company.` };
        }
        if (discordId && allCompanymen.some(p => p.discordId && p.discordId.replace(/\D/g, '') === discordId)) {
            return { status: SCRIPT_STATUS.ERROR, message: "This Discord ID is already associated with another member." };
        }

        const result = _findNodeAndPathByPathIdentifier(squad);
        if (!result) return { status: SCRIPT_STATUS.ERROR, message: `Config error: Could not find section "${squad}".` };

        const { node: targetNode, path: targetPath } = result;
        const slotBlueprintName = targetNode.useSlotsFrom || null;
        const availableSlots = THEMIS_CONFIG.SLOT_BLUEPRINTS[slotBlueprintName] || targetNode.slots || [];
        const rankSlot = availableSlots.find(s => (s.rank === rank || (s.ranks && s.ranks.includes(rank))) && (!rankTitle || s.title === rankTitle));

        if (!rankSlot) return { status: SCRIPT_STATUS.ERROR, message: `No slots defined for rank ${rank} in ${squad}.` };

        const sheetName = rankSlot.location?.sheetName || _Maia_Investigat_Progeniem(targetPath, 'sheetName');
        if (!sheetName) return { status: SCRIPT_STATUS.ERROR, message: `Config error: No sheet name defined for "${squad}".` };

        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const spreadsheetId = ss.getId();
        const sheetId = _getSheetId(ss, sheetName);

        const layoutName = rankSlot.layout || _Maia_Investigat_Progeniem(targetPath, 'layout');
        const layout = THEMIS_CONFIG.LAYOUT_BLUEPRINTS[layoutName];
        if (!layout) return { status: SCRIPT_STATUS.ERROR, message: `Config error: No layout found for "${squad}".` };

        const hasMultipleSlots = rankSlot.count > 1 || (rankSlot.location?.rows && rankSlot.location.rows.length > 1) || (rankSlot.locations && rankSlot.locations.length > 1);
        const isNowConsideredSortable = hasMultipleSlots || (rankSlot.ranks && rankSlot.ranks.length > 0);

        let allRequests = [];
        let newIdentifier;

        const getAllPossibleCoords = (slot, node) => {
            const coords = [];
            const col = node.location?.startCol || slot.location?.col;
            if (slot.locations) {
                return slot.locations.map(loc => ({ row: loc.row, col: loc.col, sheet: slot.location?.sheetName || sheetName }));
            }
            if (slot.location?.rows) {
                slot.location.rows.forEach(r => coords.push({ row: r, col: col, sheet: sheetName }));
            } else if (slot.location?.startRow && slot.location?.endRow) {
                for (let r = slot.location.startRow; r <= slot.location.endRow; r++) {
                    coords.push({ row: r, col: col, sheet: sheetName });
                }
            } else if (slot.location?.row) {
                coords.push({ row: slot.location.row, col: col, sheet: sheetName });
            }
            return coords;
        };

        if (isNowConsideredSortable) {
            const possibleCoords = getAllPossibleCoords(rankSlot, targetNode);
            if (possibleCoords.length === 0) throw new Error(`Config error: No locations defined for sortable slot in "${squad}".`);

            const membersInSlot = allCompanymen.filter(p => {
                return possibleCoords.some(coord => `${coord.sheet}|${coord.row}|${coord.col}` === p.sourceIdentifier);
            });

            if (membersInSlot.length >= possibleCoords.length) {
                throw new Error(`No available slots for ${rank} in ${squad}.`);
            }

            const newRecruitObject = { player: playerName, rank: rank, joinDate: formattedJoinDate, discordId: discordId, region: region, email: email || null, hasPassedUBT: ubtStatus, customFields: customFields || {} };
            const membersToSort = [...membersInSlot, newRecruitObject];

            const { requests: writeRequests, newIdentifier: determinedIdentifier } = _Moirae_Pangunt_Fila({
                sortedMembers: membersToSort,
                layout: layout,
                possibleCoords: possibleCoords,
                sheetId: sheetId,
                slotConfig: rankSlot
            }, true);
            allRequests.push(...writeRequests);
            newIdentifier = determinedIdentifier;

        } else { 
            const occupiedSlots = new Set(allCompanymen.map(p => p.sourceIdentifier));
            const targetCol = targetNode.location?.startCol ?? rankSlot.location?.col;
            if (targetCol === undefined) throw new Error(`Config error: No starting column defined for "${squad}".`);
            const targetRow = rankSlot.location.row;
            if (!targetRow) throw new Error(`Config error: No row defined for single billet in "${squad}".`);

            if (occupiedSlots.has(`${sheetName}|${targetRow}|${targetCol}`)) {
                 return { status: SCRIPT_STATUS.ERROR, message: `Slot for ${rank} in ${squad} is already filled.` };
            }

            const newPersonData = { player: playerName, rank: rank, joinDate: formattedJoinDate, discordId: discordId, region: region, email: email || null, hasPassedUBT: ubtStatus, customFields: {} };
            allRequests.push(..._getWriteSinglePersonRequests(newPersonData, targetRow, targetCol, layout, sheetId));
            newIdentifier = { sourceIdentifier: `${sheetName}|${targetRow}|${targetCol}` };
        }

        const logSheetName = THEMIS_CONFIG.RECRUITMENT_LOG_SHEET_NAME;
        const logSheet = ss.getSheetByName(logSheetName);
        if (logSheet) {
            const dataMap = {
                DATE: formattedJoinDate, USERNAME: playerName, DISCORD_ID: discordId ? `<@${discordId}>` : '',
                REGION: region, SQUAD: _getDisplaySectionName(squad), RECRUITER: recruiter,
                RANK: rank, EMAIL: email || '', NOTE: note || ''
            };

            const startRow = THEMIS_CONFIG.RECRUITMENT_LOG_START_ROW;
            const endRow = THEMIS_CONFIG.RECRUITMENT_LOG_END_ROW;
            const logColumns = THEMIS_CONFIG.RECRUITMENT_LOG_COLUMNS;
            const checkColumn = logColumns.DATE || 2; 

            if (!endRow) {

                throw new Error("RECRUITMENT_LOG_END_ROW must be defined in Config.js for this feature to work.");
            }

            const rangeToCheck = logSheet.getRange(startRow, checkColumn, endRow - startRow + 1, 1);
            const values = rangeToCheck.getValues();

            let targetRowIndex = -1;
            for (let i = 0; i < values.length; i++) {
                if (!values[i][0] || String(values[i][0]).trim() === '') {
                    targetRowIndex = i;
                    break;
                }
            }

            if (targetRowIndex === -1) {
                throw new Error(`The Recruitment Logbook is full within the protected range (up to row ${endRow}). Please clear old entries or extend the range.`);
            }

            const targetRow = startRow + targetRowIndex;

            const columnIndexes = Object.values(logColumns);
            const minCol = Math.min(...columnIndexes);
            const maxCol = Math.max(...columnIndexes);
            const numCols = maxCol - minCol + 1;

            const valuesToWrite = new Array(numCols).fill('');
            for (const key in dataMap) {
                if (logColumns.hasOwnProperty(key)) {
                    const colNum = logColumns[key];
                    const arrayIndex = colNum - minCol; 
                    valuesToWrite[arrayIndex] = dataMap[key];
                }
            }

            const targetRange = logSheet.getRange(targetRow, minCol, 1, numCols);
            targetRange.setValues([valuesToWrite]);
        }
        if (allRequests.length > 0) {
            Sheets.Spreadsheets.batchUpdate({ requests: allRequests }, spreadsheetId);
        }

        const [newSheetName, rowStr, colStr] = newIdentifier.sourceIdentifier.split('|');
        invalidateSpecificSheetCaches([newSheetName, logSheetName]);
        _invalidateAggregateCaches();

        const newPersonObject = {
            player: playerName, rank: rank, locationPath: squad, location: squad.split('>').pop(),
            joinDate: formattedJoinDate, email: email || null, discordId: discordId, region: region,
            sourceIdentifier: newIdentifier.sourceIdentifier, sheetName: newSheetName, row: parseInt(rowStr),
            startCol: parseInt(colStr),
            hasPassedUBT: layout?.offsets?.BTcheckbox ? ubtStatus : false,
            onLOA: false, loaData: null,
            loaNote: null, isHQ: layoutName === 'BILLET_OFFSETS', rankKey: rankTitle || null,
            customFields: customFields || {}
        };

        const { availability: newAvailabilityMap } = _Mnemosyne_Recitat();
        Aletheia_Testatur('Hebe_Initiat', 'Hebe_Initiat', { user: getCurrentUserEmail(), player: playerName, rank: rank, location: squad, discordId: discordId, region: region, email: email });
        return {
            status: SCRIPT_STATUS.SUCCESS,
            message: `Successfully recruited ${playerName} as ${rank} in ${squad}.`,
            deltaPayload: { newlyCreated: [newPersonObject], newAvailabilityMap: newAvailabilityMap }
        };
    } catch (e) {
        Aletheia_Testatur('ERROR', 'Hebe_Initiat', { message: e.message, stack: e.stack, details: JSON.stringify(details) });
        _Lethe_Delet();
        return { status: SCRIPT_STATUS.ERROR, message: e.message };
    } finally {
        lock.releaseLock();
    }
}

function _getWriteSinglePersonRequests(personData, targetRow, targetCol, layout, sheetId) {
    const requests = [];
    const offsets = layout.offsets;
    const allOffsetKeys = [...new Set([...Object.keys(offsets), ...THEMIS_CONFIG.CUSTOM_FIELDS.map(f => f.offsetKey)])];

    allOffsetKeys.forEach(key => {
        const offset = offsets[key];
        if (!offset) return;

        let cellData = null;
        switch (key) {
            case 'username':
                cellData = { userEnteredValue: { stringValue: personData.player }, note: personData.email || "" };
                break;
            case 'rank':
                const rankInfo = THEMIS_CONFIG.RANK_HIERARCHY.find(r => r.name === personData.rank);
                const rankAbbr = rankInfo ? rankInfo.abbr : "";
                cellData = { userEnteredValue: { stringValue: rankAbbr } };
                break;
            case 'region':
                cellData = { userEnteredValue: { stringValue: personData.region || "" } };
                break;
            case 'joinDate':
                const joinDateString = personData.joinDate;
                const dateObject = joinDateString ? new Date(joinDateString) : new Date();
                if (isNaN(dateObject.getTime())) {
                    cellData = { userEnteredValue: { stringValue: getFormattedDateString(new Date()) } };
                } else {
                    cellData = { userEnteredValue: { stringValue: getFormattedDateString(dateObject) } };
                }
                break;
            case 'discordId':
                const cleanId = String(personData.discordId || '').replace(/\D/g, '');
                cellData = { userEnteredValue: { stringValue: cleanId ? `<@${cleanId}>` : '' } };
                break;
            case 'LOAcheckbox':
                cellData = { userEnteredValue: { boolValue: !!personData.onLOA }, note: personData.loaNote || "" };
                break;
            case 'BTcheckbox':
                const triggerRank = THEMIS_CONFIG.UBT_SETTINGS.TRIGGER_RANK;

                const shouldBeTicked = triggerRank 
                    ? (_getRankIndex(personData.rank) >= _getRankIndex(triggerRank)) 
                    : false;

                const finalBoolValue = personData.hasPassedUBT ?? shouldBeTicked;

                cellData = { userEnteredValue: { boolValue: finalBoolValue } };
                break;
            default:
                const cf = THEMIS_CONFIG.CUSTOM_FIELDS.find(f => f.offsetKey === key);
                if (cf) {
                    let valueToWrite = null;
                    let noteToWrite = null;

                    if (personData.customFields?.[cf.key]) {
                        const cd = personData.customFields[cf.key];
                        valueToWrite = cd.value;
                        noteToWrite = (cf.transferNote && cd.note) ? cd.note : "";
                    } else if (cf.defaultValue !== undefined) {
                        valueToWrite = cf.defaultValue;
                    }

                    if (valueToWrite !== null) {
                        const userEnteredValue = (cf.type === 'integer') 
                            ? { numberValue: valueToWrite } 
                            : { stringValue: String(valueToWrite) };
                        cellData = { userEnteredValue, note: noteToWrite };
                    }
                }
                break;
        }

        if (cellData) {
            requests.push({
                updateCells: {
                    rows: [{ values: [cellData] }],
                    fields: "userEnteredValue,note",
                    start: {
                        sheetId: sheetId,
                        rowIndex: (targetRow - 1) + offset.row,
                        columnIndex: (targetCol - 1) + offset.col
                    }
                }
            });
        }
    });
    return requests;
}
function _Moirae_Pangunt_Fila({ sortedMembers, layout, possibleCoords, sheetId, slotConfig }, isRecruit = false) {
    const allRequests = [];

    for (const coord of possibleCoords) {

        const currentSheetId = _getSheetId(SpreadsheetApp.getActiveSpreadsheet(), coord.sheet);
        allRequests.push(..._getClearSinglePersonRequests(coord.row, coord.col, layout, currentSheetId, slotConfig));
    }

    const sortedDataToWrite = _Dike_Ordinat_Socios(sortedMembers);
    sortedDataToWrite.forEach((member, index) => {
        const targetCoord = possibleCoords[index];
        const currentSheetId = _getSheetId(SpreadsheetApp.getActiveSpreadsheet(), targetCoord.sheet);
        allRequests.push(..._getWriteSinglePersonRequests(member, targetCoord.row, targetCoord.col, layout, currentSheetId));
    });

    let newIdentifier = null;
    if (isRecruit) {
        const recruitObject = sortedMembers.find(sm => !sm.sourceIdentifier);
        const newPersonIndex = recruitObject ? sortedDataToWrite.findIndex(m => m.player === recruitObject.player) : -1;
        if (newPersonIndex !== -1) {
            const finalCoord = possibleCoords[newPersonIndex];
            newIdentifier = { sourceIdentifier: `${finalCoord.sheet}|${finalCoord.row}|${finalCoord.col}` };
        } else { 
            const finalCoord = possibleCoords[0];
            newIdentifier = { sourceIdentifier: `${finalCoord.sheet}|${finalCoord.row}|${finalCoord.col}` };
        }
    }

    return { requests: allRequests, newIdentifier };
}

function _performMove(personDataToMove, sourceIdentifier, newLocationPath, newRankTitle, ss) {
    const spreadsheetId = ss.getId();
    const allCompanymen = _Mnemosyne_Recitat().companymen;
    let allRequests = [];
    let newLocationDetails = {};

    const getAllPossibleCoords = (slot, node, defaultSheet) => {
        const coords = [];
        const col = node.location?.startCol || slot.location?.col;
        const sheet = slot.location?.sheetName || defaultSheet;
        if (slot.locations) { 
            return slot.locations.map(loc => ({ row: loc.row, col: loc.col, sheet: sheet }));
        }
        if (slot.location?.rows) {
            slot.location.rows.forEach(r => coords.push({ row: r, col: col, sheet: sheet }));
        } else if (slot.location?.startRow && slot.location?.endRow) {
            for (let r = slot.location.startRow; r <= slot.location.endRow; r++) {
                coords.push({ row: r, col: col, sheet: sheet });
            }
        } else if (slot.location?.row) {
            coords.push({ row: slot.location.row, col: col, sheet: sheet });
        }
        return coords;
    };

    const destResult = _findNodeAndPathByPathIdentifier(newLocationPath);
    if (!destResult) throw new Error(`Config error: Could not find destination "${newLocationPath}".`);

    const { node: destNode, path: destPath } = destResult;
    const destSheetName = _Maia_Investigat_Progeniem(destPath, 'sheetName');
    const destBlueprintName = destNode.useSlotsFrom || null;
    const destAvailableSlots = THEMIS_CONFIG.SLOT_BLUEPRINTS[destBlueprintName] || destNode.slots || [];
    const destSlot = destAvailableSlots.find(s => (s.rank === personDataToMove.rank || (s.ranks && s.ranks.includes(personDataToMove.rank))) && (!newRankTitle || s.title === newRankTitle));

    if (!destSlot) throw new Error(`No slots configured for rank ${personDataToMove.rank} in ${destNode.name}.`);

    const destLayoutName = destSlot.layout || _Maia_Investigat_Progeniem(destPath, 'layout');
    const destLayout = THEMIS_CONFIG.LAYOUT_BLUEPRINTS[destLayoutName];
    const destSheetId = _getSheetId(ss, destSheetName);

    const destPossibleCoords = getAllPossibleCoords(destSlot, destNode, destSheetName);
    if (destPossibleCoords.length === 0) throw new Error(`Config error: No locations defined for destination slot in "${destNode.name}".`);

    const destMembersInSlot = allCompanymen.filter(p => destPossibleCoords.some(coord => `${coord.sheet}|${coord.row}|${coord.col}` === p.sourceIdentifier));

    if (destMembersInSlot.length >= destPossibleCoords.length) {
        throw new Error(`No available slots for ${personDataToMove.rank} in ${destNode.name}. The section is full.`);
    }

    const destMembersToSort = [...destMembersInSlot, personDataToMove];
    const { requests: writeRequests } = _Moirae_Pangunt_Fila({
        sortedMembers: destMembersToSort,
        layout: destLayout,
        possibleCoords: destPossibleCoords,
        sheetId: destSheetId,
        slotConfig: destSlot
    });
    allRequests.push(...writeRequests);

    const sortedFinalMembers = _Dike_Ordinat_Socios(destMembersToSort);
    const newIndex = sortedFinalMembers.findIndex(p => p.player === personDataToMove.player);
    const newCoord = destPossibleCoords[newIndex];
    newLocationDetails = { newSheetName: newCoord.sheet, newRow: newCoord.row, newCol: newCoord.col };

    const sourceConfig = _findNodeBySourceIdentifier(sourceIdentifier);
    if (!sourceConfig) throw new Error(`Could not find config for source: ${sourceIdentifier}.`);

    const sourceSheetName = sourceConfig.sheetName;
    const sourceSheetId = _getSheetId(ss, sourceSheetName);
    const sourceLayout = _Themis_Praescribit_Legem(sourceConfig);
    const sourcePossibleCoords = getAllPossibleCoords(sourceConfig.slot, sourceConfig.node, sourceSheetName);

    const hasMultipleSourceSlots = sourceConfig.slot.count > 1 || (sourceConfig.slot.location?.rows && sourceConfig.slot.location.rows.length > 1) || (sourceConfig.slot.locations && sourceConfig.slot.locations.length > 1);
    const sourceIsSortable = hasMultipleSourceSlots || (sourceConfig.slot.ranks && sourceConfig.slot.ranks.length > 0);

    if (sourceIsSortable) {
        const remainingMembers = allCompanymen.filter(p =>
            p.sourceIdentifier !== sourceIdentifier &&
            sourcePossibleCoords.some(coord => `${coord.sheet}|${coord.row}|${coord.col}` === p.sourceIdentifier)
        );
        const { requests: resortRequests } = _Moirae_Pangunt_Fila({
            sortedMembers: remainingMembers,
            layout: sourceLayout,
            possibleCoords: sourcePossibleCoords,
            sheetId: sourceSheetId,
            slotConfig: sourceConfig.slot
        });
        allRequests.push(...resortRequests);
    } else { 
        const sourceRow = parseInt(sourceIdentifier.split('|')[1]);
        const sourceCol = parseInt(sourceIdentifier.split('|')[2]);
        allRequests.push(..._getClearSinglePersonRequests(sourceRow, sourceCol, sourceLayout, sourceSheetId, sourceConfig.slot));
    }

    if (allRequests.length > 0) {
        Sheets.Spreadsheets.batchUpdate({ requests: allRequests }, spreadsheetId);
        Utilities.sleep(1500);
    }

    updateLastModifiedTimestamp();
    return newLocationDetails;
}

function _getClearSinglePersonRequests(row, col, layout, sheetId, slotConfig = null) {
    const requests = [];
    const offsets = layout.offsets;
    const allOffsetKeys = [...new Set([
        ...Object.keys(offsets),
        ...(THEMIS_CONFIG.CUSTOM_FIELDS || []).map(f => f.offsetKey)
    ])];

    allOffsetKeys.forEach(key => {
        if (key === 'rank' && slotConfig && slotConfig.rank) {
            return; 
        }

        const offset = offsets[key];
        if (offset) {
            const isCheckbox = key === 'LOAcheckbox' || key === 'BTcheckbox';
            const clearValue = isCheckbox ? { boolValue: false } : null;

            requests.push({
                updateCells: {
                    rows: [{
                        values: [{
                            userEnteredValue: clearValue,
                            note: null
                        }]
                    }],
                    fields: "userEnteredValue,note",
                    start: {
                        sheetId: sheetId,
                        rowIndex: (row - 1) + offset.row,
                        columnIndex: (col - 1) + offset.col
                    }
                }
            });
        }
    });

    return requests;
}

function _getHighestApplicableTir(rankName) {
    const rankHierarchy = THEMIS_CONFIG.RANK_HIERARCHY;

    const rankIndex = rankHierarchy.findIndex(r => r.name === rankName);
    if (rankIndex === -1) {
        return null;
    }

    for (let i = rankIndex; i >= 0; i--) {
        const currentRank = rankHierarchy[i];
        const tirDays = THEMIS_CONFIG.TIME_IN_RANK_REQUIREMENTS[currentRank.name.toUpperCase()];
        if (tirDays !== undefined) {
            return { rank: currentRank.name, days: tirDays };
        }
    }
    return null;
}

function Dike_Iudicat(sourceIdentifier, newRank, newLocation, ubtApproved, email = null, rankTitle = null, grantAccess = false) {
    const lock = LockService.getScriptLock();
    if (!lock.tryLock(THEMIS_CONFIG.LOCK_TIMEOUT_MS)) {
        return { status: SCRIPT_STATUS.ERROR, message: "Server is busy. Please try again." };
    }

    try {
        const ss = SpreadsheetApp.getActiveSpreadsheet();
        if (grantAccess && email) {
            try { ss.addEditor(email); } catch (e) {
                Aletheia_Testatur('ERROR', 'Dike_Iudicat_addEditor', { message: `Failed to grant editor access for ${email}. Error: ${e.message}`, user: getCurrentUserEmail() });
            }
        }

        const allCompanymen = _Mnemosyne_Recitat().companymen;
        const oldState = _getSingleCompanyman(sourceIdentifier, ss);
        if (!oldState) return { status: SCRIPT_STATUS.ERROR, message: "Could not find the person to update. Please refresh." };

        _Nemesis_Verificat(oldState, ss);

        const oldRankIndex = _getRankIndex(oldState.rank);
        const newRankIndex = _getRankIndex(newRank);

        const personDataToMove = { ...oldState, rank: newRank };
        if (email !== null) personDataToMove.email = email;
        if (_isEmailRequiredForRank(newRank) && !personDataToMove.email) {
            return { status: SCRIPT_STATUS.ERROR, message: `Email required for ${newRank}.` };
        }

        const destResult = _findNodeAndPathByPathIdentifier(newLocation);
        if (!destResult) throw new Error(`Config error: Could not find destination "${newLocation}".`);
        const { node: destNode, path: destPath } = destResult;
        const destBlueprintName = destNode.useSlotsFrom || null;
        const destAvailableSlots = THEMIS_CONFIG.SLOT_BLUEPRINTS[destBlueprintName] || destNode.slots || [];
        const destSlot = destAvailableSlots.find(s => (s.rank === newRank || (s.ranks && s.ranks.includes(newRank))) && (!rankTitle || s.title === rankTitle));
        if (!destSlot) throw new Error(`No slot found for rank ${newRank} in ${newLocation}.`);

        const destLayoutName = destSlot.layout || _Maia_Investigat_Progeniem(destPath, 'layout');
        const destLayout = THEMIS_CONFIG.LAYOUT_BLUEPRINTS[destLayoutName];
        const destLayoutOffsets = destLayout.offsets || {};
        const destinationTracksUbt = !!destLayoutOffsets.BTcheckbox;

        let ubtStatus = oldState.hasPassedUBT;

        const triggerRank = THEMIS_CONFIG.UBT_SETTINGS.TRIGGER_RANK;
        if (triggerRank) {
            const triggerRankIndex = _getRankIndex(triggerRank);

            const isPromotionAcrossThreshold = oldRankIndex < triggerRankIndex && newRankIndex >= triggerRankIndex;
            const isCorrectiveUbtCheck = destinationTracksUbt && newRankIndex >= triggerRankIndex && !oldState.hasPassedUBT;

            if ((isPromotionAcrossThreshold || isCorrectiveUbtCheck) && !ubtApproved) {
                const ubtName = THEMIS_CONFIG.UBT_SETTINGS.NAME || 'Training';
                const promptTemplate = THEMIS_CONFIG.UBT_SETTINGS.PROMPT_MESSAGE || 'This promotion requires the member to be {name} passed. Is this correct?';
                const message = promptTemplate.replace('{name}', ubtName);
                return { status: SCRIPT_STATUS.NEEDS_CONFIRMATION, message: message };
            }
            if (ubtApproved) {
                ubtStatus = true;
            }
        }
        personDataToMove.hasPassedUBT = destinationTracksUbt ? ubtStatus : false;

        if (!_isEmailRequiredForRank(newRank)) personDataToMove.email = "";

        if (personDataToMove.customFields && THEMIS_CONFIG.CUSTOM_FIELDS) {
            const newCustomFields = {};
            THEMIS_CONFIG.CUSTOM_FIELDS.forEach(field => {
                if (destLayoutOffsets[field.offsetKey] && personDataToMove.customFields[field.key]) {
                    newCustomFields[field.key] = personDataToMove.customFields[field.key];
                }
            });
            personDataToMove.customFields = newCustomFields;
        }

        const sourceConfig = _findNodeBySourceIdentifier(sourceIdentifier);
        if (!sourceConfig) throw new Error(`Config error for source member.`);

        const isSlotSortable = (slot) => {
            if (!slot) return false;
            const hasMultiple = slot.count > 1 || (slot.location?.rows && slot.location.rows.length > 1) || (slot.locations && slot.locations.length > 1);
            return hasMultiple || (slot.ranks && slot.ranks.length > 0);
        };

        const sourceIsSortable = isSlotSortable(sourceConfig.slot);   

        let finalUpdatedPersons = [];
        let finalSheetNamesToInvalidate = new Set([oldState.sheetName]);

        if (sourceIsSortable && oldState.locationPath === newLocation && (destSlot === sourceConfig.slot)) {
            const getAllPossibleCoords = (slot, node, defaultSheet) => {
                const coords = [];
                const col = node.location?.startCol || slot.location?.col;
                const sheet = slot.location?.sheetName || defaultSheet;
                if (slot.locations) return slot.locations.map(loc => ({ row: loc.row, col: loc.col, sheet: sheet }));
                if (slot.location?.rows) slot.location.rows.forEach(r => coords.push({ row: r, col: col, sheet: sheet }));
                else if (slot.location?.startRow && slot.location?.endRow) {
                    for (let r = slot.location.startRow; r <= slot.location.endRow; r++) coords.push({ row: r, col: col, sheet: sheet });
                }
                return coords;
            };

            const possibleCoords = getAllPossibleCoords(sourceConfig.slot, sourceConfig.node, sourceConfig.sheetName);
            const membersInSlot = allCompanymen.filter(p => possibleCoords.some(coord => `${coord.sheet}|${coord.row}|${coord.col}` === p.sourceIdentifier));
     
            const personToUpdateIndex = membersInSlot.findIndex(p => p.sourceIdentifier === sourceIdentifier);
            if (personToUpdateIndex > -1) {
                membersInSlot[personToUpdateIndex] = { ...membersInSlot[personToUpdateIndex], ...personDataToMove };
            } else {
                throw new Error("Cache desync: Could not find person to update within their own slot.");
            }

            const { requests: resortRequests } = _Moirae_Pangunt_Fila({
                sortedMembers: membersInSlot,
                layout: _Themis_Praescribit_Legem(sourceConfig),
                possibleCoords: possibleCoords,
                sheetId: _getSheetId(ss, sourceConfig.sheetName),
                slotConfig: sourceConfig.slot
            });

            if (resortRequests.length > 0) {
                Sheets.Spreadsheets.batchUpdate({ requests: resortRequests }, ss.getId());
                Utilities.sleep(1500);
                updateLastModifiedTimestamp();
            }
            finalUpdatedPersons = _Dike_Ordinat_Socios(membersInSlot);

        } else {
            const newLocationDetails = _performMove(personDataToMove, sourceIdentifier, newLocation, rankTitle, ss);
            finalSheetNamesToInvalidate.add(newLocationDetails.newSheetName);

            const newSourceIdentifier = `${newLocationDetails.newSheetName}|${newLocationDetails.newRow}|${newLocationDetails.newCol}`;
            finalUpdatedPersons.push({ ...personDataToMove, sourceIdentifier: newSourceIdentifier, row: newLocationDetails.newRow, startCol: newLocationDetails.newCol });
        }

        invalidateSpecificSheetCaches([...finalSheetNamesToInvalidate]);
        _invalidateAggregateCaches();

        const { availability: newAvailabilityMap } = _Mnemosyne_Recitat();
        const newState = _Mnemosyne_Recitat().companymen.find(p => p.player === oldState.player);
        if (!newState) throw new Error(`Validation failed: Could not find ${oldState.player} after update.`);

        Aletheia_Testatur('MEMBER_UPDATE', 'Dike_Iudicat', { user: getCurrentUserEmail(), oldState: oldState, newState: newState });
        
        return {
            status: SCRIPT_STATUS.SUCCESS,
            message: _Peitho_Suadet(oldState.player, oldState.rank, newRank, oldState.location, newLocation.split('>').pop()),
            deltaPayload: { updatedPersons: finalUpdatedPersons, newAvailabilityMap: newAvailabilityMap }
        };
    } catch (e) {
        _Lethe_Delet();
        return handleError('Dike_Iudicat', e, getCurrentUserEmail());
    } finally {
        lock.releaseLock();
    }
}

function Atropos_Secat(sourceIdentifier, revokeAccess = false) {
    const lock = LockService.getScriptLock();
    if (!lock.tryLock(THEMIS_CONFIG.LOCK_TIMEOUT_MS)) {
        return { status: SCRIPT_STATUS.ERROR, message: "Server is busy. Please try again." };
    }

    try {
        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const allCompanymen = _Mnemosyne_Recitat().companymen;
        const source = allCompanymen.find(p => p.sourceIdentifier === sourceIdentifier);

        _Nemesis_Verificat(source, ss);

        if (revokeAccess && source.email) {
            try {
                if (ss.getOwner().getEmail().toLowerCase() !== source.email.toLowerCase()) {
                    ss.removeEditor(source.email);
                }
            } catch (e) {
                Aletheia_Testatur('ERROR', 'Atropos_Secat_removeEditor', { message: `Failed to revoke editor access for ${source.email}. Error: ${e.message}`, user: getCurrentUserEmail() });
            }
        }

        const config = _findNodeBySourceIdentifier(sourceIdentifier);
        const sourceLayout = _Themis_Praescribit_Legem(config);
        const sourceSheetName = config.sheetName;
        const sourceSheetId = _getSheetId(ss, sourceSheetName);

        let allRequests = [];
        let sortedAndUpdatedMembers = [];

        const slot = config.slot;
        const hasMultipleSlots = slot.count > 1 || (slot.location?.rows && slot.location.rows.length > 1) || (slot.locations && slot.locations.length > 1);
        const isNowConsideredSortable = hasMultipleSlots || (slot.ranks && slot.ranks.length > 0);

        const getAllPossibleCoords = (slot, node, defaultSheet) => {
            const coords = [];
            const col = node.location?.startCol || slot.location?.col;
            const sheet = slot.location?.sheetName || defaultSheet;
            if (slot.locations) return slot.locations.map(loc => ({ row: loc.row, col: loc.col, sheet: sheet }));
            if (slot.location?.rows) slot.location.rows.forEach(r => coords.push({ row: r, col: col, sheet: sheet }));
            else if (slot.location?.startRow && slot.location?.endRow) {
                for (let r = slot.location.startRow; r <= slot.location.endRow; r++) coords.push({ row: r, col: col, sheet: sheet });
            }
            return coords;
        };

        if (isNowConsideredSortable) {
            const possibleCoords = getAllPossibleCoords(slot, config.node, sourceSheetName);
            const remainingMembers = allCompanymen.filter(p =>
                p.sourceIdentifier !== source.sourceIdentifier &&
                possibleCoords.some(coord => `${coord.sheet}|${coord.row}|${coord.col}` === p.sourceIdentifier)
            );

            const { requests: resortRequests } = _Moirae_Pangunt_Fila({ sortedMembers: remainingMembers, layout: sourceLayout, possibleCoords: possibleCoords, sheetId: sourceSheetId, slotConfig: slot });
            allRequests.push(...resortRequests);

            sortedAndUpdatedMembers = _Dike_Ordinat_Socios(remainingMembers).map((member, index) => {
                const newCoord = possibleCoords[index];
                return { ...member, row: newCoord.row, startCol: newCoord.col, sourceIdentifier: `${newCoord.sheet}|${newCoord.row}|${newCoord.col}` };
            });

        } else {
            const sourceRow = parseInt(sourceIdentifier.split('|')[1]);
            const sourceCol = parseInt(sourceIdentifier.split('|')[2]);
            allRequests.push(..._getClearSinglePersonRequests(sourceRow, sourceCol, sourceLayout, sourceSheetId, config.slot));
        }

        if (allRequests.length > 0) {
            Sheets.Spreadsheets.batchUpdate({ requests: allRequests }, ss.getId());
            updateLastModifiedTimestamp();
        }

        invalidateSpecificSheetCaches([source.sheetName]);
        _invalidateAggregateCaches();

        const { availability: newAvailabilityMap } = _Mnemosyne_Recitat();

        Aletheia_Testatur('Atropos_Secat', 'Atropos_Secat', { user: getCurrentUserEmail(), deletedMember: source });

        return {
            status: SCRIPT_STATUS.SUCCESS,
            message: `Successfully deleted ${source.player}.`,
            deltaPayload: {
                deletedIdentifier: sourceIdentifier,
                updatedPersons: sortedAndUpdatedMembers,
                newAvailabilityMap: newAvailabilityMap
            }
        };
    } catch (e) {
        Aletheia_Testatur('ERROR', 'Atropos_Secat', { message: e.message, stack: e.stack, user: getCurrentUserEmail() });
        _Lethe_Delet();
        return { status: SCRIPT_STATUS.ERROR, message: e.message };
    } finally {
        lock.releaseLock();
    }
}

function Fides_Signat(playerObject, email) {
    try {
        if (!playerObject || !playerObject.sourceIdentifier) {
            throw new Error("Invalid player data received. Please refresh and try again.");
        }
        const sourceIdentifier = playerObject.sourceIdentifier;

        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const sheet = ss.getSheetByName(playerObject.sheetName);
        if (!sheet) throw new Error(`Sheet "${playerObject.sheetName}" not found.`);

        const config = _findNodeBySourceIdentifier(sourceIdentifier);
        if (!config || !config.slot) throw new Error(`Could not find configuration for member.`);

        const layout = _Themis_Praescribit_Legem(config);
        if (!layout.offsets || !layout.offsets.username) throw new Error(`"username" offset not defined in the layout.`);

        const usernameOffset = layout.offsets.username;
        const targetRow = playerObject.row + usernameOffset.row;
        const targetCol = playerObject.startCol + usernameOffset.col;
        const usernameCell = sheet.getRange(targetRow, targetCol);

        usernameCell.setNote(email);

        invalidateSpecificSheetCaches([playerObject.sheetName]);
        updateLastModifiedTimestamp();

        return {
            status: SCRIPT_STATUS.SUCCESS,
            message: "Email saved successfully."
        };
    } catch (e) {
        Aletheia_Testatur('ERROR', 'Fides_Signat', { message: e.message, stack: e.stack, user: getCurrentUserEmail() });
        return {
            status: SCRIPT_STATUS.ERROR,
            message: "Failed to save email: " + e.message
        };
    }
}

function clearWebhookQueue() {
  const cacheKey = 'webhook_retry_queue_v1';
  CacheService.getScriptCache().remove(cacheKey);
  Logger.log('Success', 'The webhook retry queue has been cleared.');
}
function _sendWebhookNotification(payload) {
    _Iris_Volat(payload);
}

function _Nemesis_Verificat(sourceFromCache, ss) {
  if (!sourceFromCache) {
    throw new Error("Could not find the specified person in the cache. Please refresh.");
  }

  const { sourceIdentifier, player } = sourceFromCache;

  const config = _findNodeBySourceIdentifier(sourceIdentifier);
  if (!config) throw new Error(`Configuration error for member at ${sourceIdentifier}.`);

  const layoutName = config.slot.layout || _Maia_Investigat_Progeniem(config.fullPath, 'layout');
  const layout = THEMIS_CONFIG.LAYOUT_BLUEPRINTS[layoutName];
  if (!layout || !layout.offsets.username) throw new Error(`Layout or username offset missing for member's slot.`);

  const [sheetName, rowStr, colStr] = sourceIdentifier.split('|');
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error(`Sheet "${sheetName}" not found.`);

  const usernameOffset = layout.offsets.username;
  const liveUsernameCell = sheet.getRange(parseInt(rowStr) + usernameOffset.row, parseInt(colStr) + usernameOffset.col);
  const liveUsername = liveUsernameCell.getValue().toString().trim();

  if (liveUsername !== player.trim()) {
    _Lethe_Delet();
    throw new Error(`Data mismatch detected. You tried to act on "${player}", but "${liveUsername || 'an empty cell'}" is now in that slot. The spreadsheet has been updated. Please refresh and try again.`);
  }
}
