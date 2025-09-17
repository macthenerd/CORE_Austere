# database_operations/smart_extractor.py

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

class SmartContentExtractor:
    """
    Intelligent content extractor that builds dynamic schema based on document patterns
    """
    
    def __init__(self):
        # Pattern definitions for various data types
        self.patterns = {
            'classification': [
                r'Classification:\s*([A-Z//\s]+)',
                r'CLASSIFICATION:\s*([A-Z//\s]+)', 
                r'(?:^|\n)\s*([A-Z]+//[A-Z\s/]+)',
                r'(?:^|\n)\s*(UNCLASSIFIED|CONFIDENTIAL|SECRET|TOP\s*SECRET)(?://[A-Z\s/]+)?'
            ],
            'date_time': [
                r'Date[/\s]*Time[^:]*:\s*([^\n]+)',
                r'Date:\s*([^\n]+)',
                r'Time:\s*([^\n]+)',
                r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2}-\d{4})'
            ],
            'unit': [
                r'Reporting\s+Unit:\s*([^\n]+)',
                r'Unit:\s*([^\n]+)',
                r'From:\s*([^\n]+)',
                r'(\d+(?:st|nd|rd|th)\s+[A-Za-z\s]+(?:Battalion|Regiment|Division|Detachment|Company|Brigade))',
                r'([A-Z]+\s+\d+[A-Z]*)'
            ],
            'location_mgrs': [
                r'Location[^:]*MGRS[^:]*:\s*([A-Z0-9\s]+)',
                r'MGRS[^:]*:\s*([A-Z0-9\s]+)',
                r'Grid[^:]*:\s*([A-Z0-9\s]+)',
                r'\b(\d{1,2}[A-Z]{3}\d{4,10})\b'
            ],
            'location_name': [
                r'Location[^:]*:\s*([^(\n]+)(?:\([^)]*\))?',
                r'Area[^:]*:\s*([^\n]+)',
                r'Region[^:]*:\s*([^\n]+)',
                r'(?:near|at|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            ],
            'analyst': [
                r'Analyst:\s*([^\n]+)',
                r'Prepared\s+by:\s*([^\n]+)',
                r'Author:\s*([^\n]+)',
                r'By:\s*([A-Z]\.\s*[A-Z][a-z]+)'
            ],
            'summary': [
                r'Executive\s+Summary[:\s]*\n([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)',
                r'Summary[:\s]*\n([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)',
                r'SUMMARY[:\s]*\n([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)'
            ],
            'assessment': [
                r'Assessment[:\s]*\n([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)',
                r'Analysis[:\s]*\n([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)',
                r'Conclusion[:\s]*\n([^\n]+(?:\n(?![\w\s]*:)[^\n]*)*)'
            ],
            'recommendations': [
                r'Recommendations?[:\s]*\n((?:\d+\..*?\n?)*)',
                r'Actions?[:\s]*\n((?:\d+\..*?\n?)*)',
                r'Next\s+Steps[:\s]*\n((?:\d+\..*?\n?)*)'
            ],
            'confidence': [
                r'(High|Medium|Moderate|Low)\s+confidence',
                r'Confidence:\s*([^\n]+)',
                r'Reliability:\s*([^\n]+)'
            ],
            'source_type': [
                r'(HUMINT|SIGINT|IMINT|GEOINT|OSINT|UAV|ELINT)',
                r'Source:\s*([^\n]+)',
                r'Intel\s+Type:\s*([^\n]+)'
            ]
        }
        
        # Value cleaning patterns
        self.cleaners = {
            'classification': lambda x: x.strip().upper(),
            'date_time': self.parse_datetime,
            'location_mgrs': lambda x: re.sub(r'\s+', '', x.upper()),
            'location_name': lambda x: x.strip().title(),
            'analyst': lambda x: x.strip().title(),
            'confidence': lambda x: x.strip().title(),
            'source_type': lambda x: x.strip().upper()
        }

    def parse_datetime(self, date_str: str) -> str:
        """Parse various date/time formats into ISO format"""
        date_str = date_str.strip()
        
        # Common patterns
        patterns = [
            ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S'),
            ('%Y-%m-%d', '%Y-%m-%d'),
            ('%m/%d/%Y', '%Y-%m-%d'),
            ('%d/%m/%Y', '%Y-%m-%d'),
            ('%m-%d-%Y', '%Y-%m-%d'),
            ('%d-%m-%Y', '%Y-%m-%d'),
        ]
        
        for input_pattern, output_pattern in patterns:
            try:
                parsed = datetime.strptime(date_str, input_pattern)
                return parsed.strftime(output_pattern)
            except ValueError:
                continue
        
        return date_str  # Return original if can't parse

    def extract_structured_data(self, text: str, filename: str = "") -> Dict[str, Any]:
        """Extract structured data from document text"""
        
        extracted = {
            'raw_extractions': {},
            'structured_fields': {},
            'confidence_scores': {},
            'document_type': self.classify_document_type(text),
            'extraction_metadata': {
                'filename': filename,
                'extraction_time': datetime.now().isoformat(),
                'text_length': len(text)
            }
        }
        
        # Extract all patterns
        for field_type, patterns in self.patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if found:
                    matches.extend(found)
            
            if matches:
                # Clean and deduplicate matches
                cleaned = []
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else (match[1] if len(match) > 1 else "")
                    
                    if field_type in self.cleaners:
                        match = self.cleaners[field_type](match)
                    else:
                        match = match.strip()
                    
                    if match and match not in cleaned:
                        cleaned.append(match)
                
                extracted['raw_extractions'][field_type] = cleaned
                
                # Take best match (usually first, most specific)
                if cleaned:
                    extracted['structured_fields'][field_type] = cleaned[0]
                    extracted['confidence_scores'][field_type] = self.calculate_confidence(field_type, cleaned[0], text)

        # Post-process and enhance
        extracted = self.post_process_extractions(extracted, text)
        
        return extracted

    def classify_document_type(self, text: str) -> str:
        """Classify the type of document based on content patterns"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['intelligence', 'intel', 'assessment', 'analysis']):
            if any(word in text_lower for word in ['summary', 'sitrep', 'situation']):
                return 'intelligence_summary'
            elif any(word in text_lower for word in ['assessment', 'analysis']):
                return 'intelligence_assessment'
            else:
                return 'intelligence_report'
        elif any(word in text_lower for word in ['patrol', 'mission', 'operation']):
            return 'mission_report'
        elif any(word in text_lower for word in ['incident', 'event', 'contact']):
            return 'incident_report'
        elif any(word in text_lower for word in ['brief', 'briefing']):
            return 'briefing'
        else:
            return 'general_document'

    def calculate_confidence(self, field_type: str, value: str, full_text: str) -> float:
        """Calculate confidence score for extracted field"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on context
        if field_type == 'classification' and 'classification:' in full_text.lower():
            confidence += 0.3
        elif field_type == 'date_time' and any(word in full_text.lower() for word in ['date', 'time']):
            confidence += 0.2
        elif field_type == 'unit' and 'unit' in full_text.lower():
            confidence += 0.3
        elif field_type == 'location_mgrs' and 'mgrs' in full_text.lower():
            confidence += 0.4
        
        # Decrease confidence for very short or generic values
        if len(value) < 3:
            confidence -= 0.2
        
        return min(1.0, max(0.1, confidence))

    def post_process_extractions(self, extracted: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Post-process extractions to enhance and validate"""
        
        # Combine date and time if separate
        if 'date_time' not in extracted['structured_fields']:
            date_parts = []
            if 'date' in extracted['raw_extractions']:
                date_parts.extend(extracted['raw_extractions']['date'])
            if 'time' in extracted['raw_extractions']:
                date_parts.extend(extracted['raw_extractions']['time'])
            
            if date_parts:
                combined = ' '.join(date_parts[:2])  # Take first date and time
                extracted['structured_fields']['date_time'] = self.parse_datetime(combined)

        # Extract key topics and themes
        extracted['structured_fields']['key_themes'] = self.extract_themes(text)
        
        # Extract entities (people, places, organizations)
        extracted['structured_fields']['entities'] = self.extract_entities(text)
        
        # Generate summary statistics
        extracted['extraction_metadata']['fields_found'] = len(extracted['structured_fields'])
        extracted['extraction_metadata']['avg_confidence'] = (
            sum(extracted['confidence_scores'].values()) / len(extracted['confidence_scores'])
            if extracted['confidence_scores'] else 0.0
        )
        
        return extracted

    def extract_themes(self, text: str) -> List[str]:
        """Extract key themes and topics from text"""
        themes = []
        text_lower = text.lower()
        
        theme_keywords = {
            'security': ['security', 'threat', 'hostile', 'enemy', 'insurgent'],
            'logistics': ['supply', 'resupply', 'convoy', 'logistics', 'equipment'],
            'surveillance': ['uav', 'surveillance', 'observation', 'monitoring', 'isr'],
            'communications': ['comms', 'radio', 'frequency', 'signal', 'transmission'],
            'movement': ['movement', 'patrol', 'vehicle', 'activity', 'formation'],
            'intelligence': ['intel', 'humint', 'sigint', 'imint', 'analysis']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:5]  # Limit to top 5 themes

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {
            'people': [],
            'places': [],
            'organizations': [],
            'equipment': []
        }
        
        # Simple pattern-based entity extraction
        # People (names with initials)
        people_patterns = [
            r'\b[A-Z]\.\s*[A-Z][a-z]+\b',
            r'\b(?:Analyst|Officer|Commander|Agent):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in people_patterns:
            matches = re.findall(pattern, text)
            entities['people'].extend(matches)
        
        # Places (capitalized words after location indicators)
        place_patterns = [
            r'(?:Highway|Route|Road)\s+(\d+)',
            r'(?:near|at|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        ]
        
        for pattern in place_patterns:
            matches = re.findall(pattern, text)
            entities['places'].extend(matches)
        
        # Equipment/Systems
        equipment_patterns = [
            r'\b(UAV|UAS|drone)s?\b',
            r'\b(\d+\.\d+\s*MHz)\b',
            r'\b(thermal\s+imagery|night\s+vision|radio)\b'
        ]
        
        for pattern in equipment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['equipment'].extend(matches)
        
        # Clean and deduplicate
        for entity_type in entities:
            entities[entity_type] = list(set([e.strip() for e in entities[entity_type] if e.strip()]))[:5]
        
        return entities

    def format_for_database(self, extracted_data: Dict[str, Any], original_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Format extracted data for database storage"""
        
        # Start with original fields
        result = original_fields.copy()
        
        # Map extracted fields to database fields
        field_mapping = {
            'classification': 'highest_classification',
            'date_time': 'timeframes',
            'location_name': 'locations',
            'unit': 'subjects',
            'key_themes': 'topics',
            'analyst': 'caveats',  # Store analyst info in caveats for now
        }
        
        structured = extracted_data.get('structured_fields', {})
        
        for extracted_field, db_field in field_mapping.items():
            if extracted_field in structured and structured[extracted_field]:
                if extracted_field == 'key_themes':
                    result[db_field] = '|'.join(structured[extracted_field])
                else:
                    result[db_field] = str(structured[extracted_field])
        
        # Enhance MGRS field
        if 'location_mgrs' in structured:
            existing_mgrs = result.get('MGRS', '')
            new_mgrs = structured['location_mgrs']
            if existing_mgrs and new_mgrs not in existing_mgrs:
                result['MGRS'] = f"{existing_mgrs}|{new_mgrs}"
            elif not existing_mgrs:
                result['MGRS'] = new_mgrs
        
        # Store extraction metadata as JSON in a new field
        result['extraction_metadata'] = json.dumps({
            'document_type': extracted_data.get('document_type'),
            'confidence_scores': extracted_data.get('confidence_scores', {}),
            'entities': extracted_data.get('structured_fields', {}).get('entities', {}),
            'extraction_time': extracted_data.get('extraction_metadata', {}).get('extraction_time')
        })
        
        return result
